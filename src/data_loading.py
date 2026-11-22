"""Leitura dos dados originais (data/raw/).

Nenhuma função daqui altera os arquivos em disco: elas apenas leem e devolvem
DataFrames. A limpeza fica em `src.cleaning`.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd
import xlrd

from src import config

# Leitura das planilhas da CONAB: quantas linhas iniciais formam o cabeçalho
# de cada aba e quantas contêm o título (produto, safra e local).
LINHAS_CABECALHO = 14
LINHAS_TITULO = 7

# Conferência da unidade: produtividades abaixo do mínimo são erro de leitura
# ou de preenchimento, e a saca implícita pode diferir da declarada até 5%.
PRODUTIVIDADE_MINIMA = 200
TOLERANCIA_UNIDADE = 0.05

MESES = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12,
}

UFS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
    "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}


def carregar_icb(caminho: Path = config.ARQUIVO_ICB) -> pd.DataFrame:
    """Lê a planilha ICB_DADOS_2026.xlsx e devolve os dados brutos.

    Deve:
    - ler a única aba do arquivo com `pd.read_excel` (engine openpyxl);
    - manter apenas as colunas definidas em `config` (COL_MES, COL_DATA_COLETA,
      COL_MERCADO, COL_PRODUTO, COL_MARCA, COL_PRECO, COL_QUANTIDADE, COL_PPK),
      descartando colunas vazias extras que existam na planilha;
    - NÃO fazer limpeza aqui (nomes, tipos, faltantes ficam em `cleaning`).

    Observação: as datas podem vir como número serial do Excel; a conversão
    fica em `cleaning.converter_tipos`.

    Returns:
        DataFrame com uma linha por coleta de preço (~46 mil linhas).
    """
    raise NotImplementedError


def listar_arquivos_conab(diretorio: Path = config.DIR_CONAB) -> list[Path]:
    """Lista as planilhas da CONAB disponíveis em data/raw/conab/.

    As planilhas ficam em uma subpasta por produto (ex.: conab/arroz/,
    conab/feijao/). Busca recursivamente os arquivos .xls/.xlsx (ignorando o
    README.md e temporários do Excel), para que o notebook 03 saiba quais
    produtos já foram baixados.
    """
    return sorted(
        arquivo
        for arquivo in Path(diretorio).rglob("*")
        if arquivo.is_file()
        and arquivo.suffix.lower() in {".xls", ".xlsx"}
        and not arquivo.name.startswith("~$")
    )


def _normalizar(texto: str) -> str:
    """Remove acentos, passa para maiúsculas e reduz espaços."""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento).strip().upper()


def _texto_linha(aba: xlrd.sheet.Sheet, linha: int) -> str:
    """Junta os textos e números de uma linha, já normalizados."""
    partes = []
    for celula in aba.row(linha):
        if celula.ctype == xlrd.XL_CELL_TEXT:
            partes.append(celula.value)
        elif celula.ctype == xlrd.XL_CELL_NUMBER:
            partes.append(f"{celula.value:g}")
    return _normalizar(" ".join(partes))


def _extrair_periodo(aba: xlrd.sheet.Sheet, datemode: int) -> pd.Period | None:
    """Lê o mês de referência dos preços ("A preços de" ou "Mês/Ano")."""
    for linha in range(min(LINHAS_CABECALHO, aba.nrows)):
        texto = _texto_linha(aba, linha)
        rotulo = re.search(r"A PRECOS DE:?|MES/ANO:?", texto)
        if not rotulo:
            continue

        for celula in aba.row(linha):
            if celula.ctype == xlrd.XL_CELL_DATE:
                ano, mes, *_ = xlrd.xldate_as_tuple(celula.value, datemode)
                return pd.Period(year=ano, month=mes, freq="M")

        resto = texto[rotulo.end():]
        numerico = re.search(r"\d{1,2}\s*[./-]+\s*(\d{1,2})\s*[./-]+\s*(\d{4}|\d{2})\b", resto)
        if numerico:
            mes, ano = int(numerico.group(1)), int(numerico.group(2))
        else:
            por_nome = re.search(r"\b([A-Z]{3})[A-Z]*\s*[/\- ]\s*(\d{4}|\d{2})\b", resto)
            if not por_nome or por_nome.group(1) not in MESES:
                continue
            mes, ano = MESES[por_nome.group(1)], int(por_nome.group(2))
        if 1 <= mes <= 12:
            return pd.Period(year=ano + 2000 if ano < 100 else ano, month=mes, freq="M")
    return None


def _extrair_kg_unidade(aba: xlrd.sheet.Sheet) -> float:
    """Descobre quantos kg tem a unidade de comercialização (saca de 50 ou 60)."""
    textos = [_texto_linha(aba, i) for i in range(min(LINHAS_CABECALHO, aba.nrows))]
    for texto in textos:
        achado = re.search(
            r"(?:R\$\s*/\s*(?:SC\s*)?|CUSTO\s*/\s*(?:SACO\s*\([^)]*\)\s*-\s*)?|KG/SC\s*)(\d+)\s*KG",
            texto,
        )
        if achado:
            return float(achado.group(1))
    for texto in textos:
        achado = re.search(r"UNIDADE DE (?:COMERCIALIZACAO|PRODUTO):?\s*(\d+)\s*KG", texto)
        if achado:
            return float(achado.group(1))
    return float("nan")


def _extrair_produtividade(aba: xlrd.sheet.Sheet) -> float:
    """Lê a produtividade em kg/ha, usada para conferir a unidade."""
    for linha in range(min(LINHAS_CABECALHO, aba.nrows)):
        texto = _texto_linha(aba, linha)
        if "PRODUTIVIDADE" not in texto:
            continue
        # Ignora o tamanho da saca em textos como "sc 60 kg/ha".
        achado = re.search(r"(?<!SC )(?<![\d.,])(\d[\d.]*(?:,\d+)?)\s*KG", texto)
        if achado:
            return float(achado.group(1).replace(".", "").replace(",", "."))
    return float("nan")


def _separar_nome_aba(nome: str) -> dict:
    """Separa município, UF, ano e variante a partir do nome da aba."""
    ano = re.search(r"(?<!\d)(\d{4})(?!\d)", nome)
    uf = next((t for t in re.findall(r"[A-Z]{2}", nome) if t in UFS and re.search(rf"(?<![A-Za-z]){t}(?![A-Za-z])", nome)), None)
    resto = nome
    if ano:
        resto = resto.replace(ano.group(1), " ")
    if uf:
        resto = re.sub(rf"(?<![A-Za-z]){uf}(?![A-Za-z])", " ", resto)
    prefixo = re.match(r"\s*(AE|CM|PD|\dª)\s*-?\s*", resto)
    variante = [prefixo.group(1)] if prefixo else []
    if prefixo:
        resto = resto[prefixo.end():]
    sufixo = re.search(r"-\s*(S\.Mec|Mec)\s*$", resto.strip(" -"))
    if sufixo:
        variante.append(sufixo.group(1))
        resto = resto.strip(" -")[: sufixo.start()]
    return {
        "local": re.sub(r"\s+", " ", resto.strip(" -")),
        "uf": uf,
        "ano": int(ano.group(1)) if ano else None,
        "variante": "/".join(variante) or None,
    }


def _titulo_diverge(aba: xlrd.sheet.Sheet, local: str) -> bool:
    """Indica se o título interno da aba cita outro município."""
    cabecalho = "".join(
        _texto_linha(aba, i) for i in range(min(LINHAS_TITULO, aba.nrows))
    ).replace(" ", "")
    chave = re.sub(r"[^A-Z ]", " ", _normalizar(local))
    termos = [t for t in chave.split() if len(t) >= 4]
    if not termos:
        return False
    compacto = "".join(chave.split())
    return compacto not in cabecalho and not any(t in cabecalho for t in termos)


def _ler_aba_conab(aba: xlrd.sheet.Sheet, datemode: int, produto: str, planilha: str) -> dict:
    """Extrai uma linha da tabela longa a partir de uma aba de custo."""
    registro = {"produto": produto, "planilha": planilha, "aba": aba.name}
    registro.update(_separar_nome_aba(aba.name))
    registro["regiao"] = f"{registro['local']}-{registro['uf']}"

    titulo = " ".join(_texto_linha(aba, i) for i in range(min(LINHAS_TITULO, aba.nrows)))
    tipo = re.search(r"AGRICULTURA (FAMILIAR|EMPRESARIAL)", titulo)
    safra = re.search(r"\d{4}/\d{2,4}", titulo)
    registro["tipo_empreendimento"] = tipo.group(0).title() if tipo else None
    registro["safra"] = safra.group(0) if safra else None
    registro["periodo"] = _extrair_periodo(aba, datemode)
    registro["titulo_divergente"] = _titulo_diverge(aba, registro["local"])

    numeros = []
    custo_total = []
    for linha in range(aba.nrows):
        valores = [c.value for c in aba.row(linha) if c.ctype == xlrd.XL_CELL_NUMBER]
        numeros.extend(round(v, 2) for v in valores if v)
        if re.search(r"CUSTO\s+TOTAL", _texto_linha(aba, linha)):
            custo_total = valores
    registro["assinatura"] = hash(tuple(numeros))

    registro["custo_area"] = custo_total[0] if len(custo_total) >= 2 else float("nan")
    registro["custo_unidade_original"] = custo_total[1] if len(custo_total) >= 2 else float("nan")
    registro["produtividade_kg_ha"] = float("nan")

    if produto == "Leite":
        registro["base_area"] = "R$/ano"
        registro["kg_unidade"] = 1.0
        registro["unidade"] = "R$/l"
    else:
        registro["base_area"] = "R$/ha"
        registro["kg_unidade"] = _extrair_kg_unidade(aba)
        registro["produtividade_kg_ha"] = _extrair_produtividade(aba)
        registro["unidade"] = "R$/kg"
    registro["custo"] = registro["custo_unidade_original"] / registro["kg_unidade"]
    return registro


def _marcar_problemas(tabela: pd.DataFrame) -> pd.DataFrame:
    """Preenche `problema` e `valido` sem alterar os valores lidos."""
    tabela = tabela.copy()
    repetida = tabela.duplicated("assinatura", keep=False)
    # Aba repetida só é considerada cópia quando o título cita outro local.
    copia = repetida & tabela["titulo_divergente"]
    # No mesmo local, a aba mais recente com dados iguais repete a anterior.
    repete_ano = (
        tabela.sort_values("ano")
        .duplicated(["assinatura", "regiao"], keep="first")
        .reindex(tabela.index)
    )

    # Saca declarada x saca implícita (produtividade * custo por saca / custo por ha).
    kg_implicito = (
        tabela["produtividade_kg_ha"].where(tabela["produtividade_kg_ha"] >= PRODUTIVIDADE_MINIMA)
        * tabela["custo_unidade_original"]
        / tabela["custo_area"]
    )
    unidade_inconsistente = (kg_implicito / tabela["kg_unidade"] - 1).abs() > TOLERANCIA_UNIDADE

    motivos = pd.DataFrame(index=tabela.index)
    motivos["sem_custo_total"] = tabela["custo_area"].isna()
    motivos["sem_data"] = tabela["periodo"].isna()
    motivos["sem_unidade"] = tabela["custo"].isna() & tabela["custo_area"].notna()
    motivos["unidade_inconsistente"] = unidade_inconsistente
    motivos["copia_de_outra_aba"] = copia
    motivos["repete_ano_anterior"] = repete_ano & ~copia
    motivos["titulo_divergente"] = tabela["titulo_divergente"] & ~copia
    motivos["dados_repetidos"] = repetida & ~copia & ~repete_ano

    tabela["problema"] = motivos.apply(
        lambda linha: ";".join(nome for nome, ativo in linha.items() if ativo) or None,
        axis=1,
    )
    tabela["valido"] = ~motivos[
        [
            "sem_custo_total",
            "sem_data",
            "sem_unidade",
            "unidade_inconsistente",
            "copia_de_outra_aba",
            "repete_ano_anterior",
        ]
    ].any(axis=1)
    return tabela.drop(columns=["assinatura", "titulo_divergente"])


def carregar_conab(produto: str, diretorio: Path = config.DIR_CONAB) -> pd.DataFrame:
    """Lê as planilhas de custo de produção da CONAB de um produto.

    Decisão 5: só faz sentido para os produtos em `config.PRODUTOS_CONAB`
    (Arroz, Feijão, Café, Leite); para outros lança ValueError.

    Devolve uma tabela longa, com uma linha por aba (local + ano/safra):
    - `periodo`: mês de referência dos preços da planilha;
    - `regiao`, `local`, `uf`, `variante`, `tipo_empreendimento`, `safra`, `ano`;
    - `custo`: custo total em `unidade` (R$/kg ou, no leite, R$/l);
    - `custo_area`: custo total em `base_area` (R$/ha ou, no leite, R$/ano);
    - `custo_unidade_original` e `kg_unidade`: valor por saca e tamanho da saca;
    - `valido` e `problema`: resultado das verificações de qualidade.

    Nenhum valor é corrigido ou imputado: abas com problema continuam na
    tabela, marcadas, para que o descarte fique documentado.
    """
    if produto not in config.PRODUTOS_CONAB:
        raise ValueError(f"Produto sem dados da CONAB: {produto!r}")

    pasta = Path(diretorio) / config.PASTAS_CONAB[produto]
    arquivos = listar_arquivos_conab(pasta)
    if not arquivos:
        raise FileNotFoundError(f"Nenhuma planilha encontrada em {pasta}")

    registros = []
    for arquivo in arquivos:
        livro = xlrd.open_workbook(arquivo)
        for aba in livro.sheets():
            if _normalizar(aba.name) == "INDICE":
                continue
            registros.append(_ler_aba_conab(aba, livro.datemode, produto, arquivo.name))

    tabela = _marcar_problemas(pd.DataFrame(registros))
    tabela["periodo"] = pd.PeriodIndex(tabela["periodo"], freq="M")
    return tabela.sort_values(["planilha", "regiao", "ano", "aba"]).reset_index(drop=True)


def carregar_conab_completo(diretorio: Path = config.DIR_CONAB) -> pd.DataFrame:
    """Junta a tabela longa de todos os produtos em `config.PRODUTOS_CONAB`."""
    return pd.concat(
        [carregar_conab(produto, diretorio) for produto in config.PRODUTOS_CONAB],
        ignore_index=True,
    )


def _abrir_planilha_leite(diretorio: Path) -> xlrd.book.Book:
    """Abre a planilha de leite definida em `config.SERIES_CONAB`."""
    pasta = Path(diretorio) / config.PASTAS_CONAB["Leite"]
    return xlrd.open_workbook(pasta / config.SERIES_CONAB["Leite"]["planilha"])


def inspecionar_abas_leite(abas: list[str], diretorio: Path = config.DIR_CONAB) -> pd.DataFrame:
    """Mostra município do título, produção e custo de abas da planilha de leite."""
    livro = _abrir_planilha_leite(diretorio)
    linhas = []
    for nome in abas:
        aba = livro.sheet_by_name(nome)
        registro = {"aba": nome}
        for i in range(aba.nrows):
            texto = _texto_linha(aba, i)
            numeros = [c.value for c in aba.row(i) if c.ctype == xlrd.XL_CELL_NUMBER]
            municipio = re.search(r"MUNICIPIO:\s*(.+)", texto)
            if municipio:
                registro["municipio_no_titulo"] = municipio.group(1).strip()
            elif texto.startswith("PRODUCAO DE LEITE") and numeros:
                registro["producao_l_dia"] = numeros[0]
            elif "CUSTO TOTAL" in texto and len(numeros) >= 2:
                registro["custo_r_por_ano"] = numeros[0]
                registro["custo_r_por_litro"] = numeros[1]
        linhas.append(registro)
    return pd.DataFrame(linhas)


def diferencas_entre_abas_leite(
    aba_a: str,
    aba_b: str,
    diretorio: Path = config.DIR_CONAB,
) -> pd.DataFrame:
    """Compara duas abas de leite célula por célula e lista as diferenças.

    `linha` e `coluna` seguem a numeração do Excel (começando em 1).
    """
    livro = _abrir_planilha_leite(diretorio)
    a, b = livro.sheet_by_name(aba_a), livro.sheet_by_name(aba_b)

    def valor(aba: xlrd.sheet.Sheet, linha: int, coluna: int):
        return aba.cell_value(linha, coluna) if linha < aba.nrows and coluna < aba.row_len(linha) else ""

    diferencas = [
        {"linha": i + 1, "coluna": j + 1, aba_a: valor(a, i, j), aba_b: valor(b, i, j)}
        for i in range(max(a.nrows, b.nrows))
        for j in range(max(a.ncols, b.ncols))
        if valor(a, i, j) != valor(b, i, j)
    ]
    return pd.DataFrame(diferencas, columns=["linha", "coluna", aba_a, aba_b])


def selecionar_series_conab(tabela: pd.DataFrame) -> pd.DataFrame:
    """Filtra as abas válidas das séries de `config.SERIES_CONAB` na janela da base."""
    partes = []
    for produto, serie in config.SERIES_CONAB.items():
        filtro = (
            (tabela["produto"] == produto)
            & (tabela["planilha"] == serie["planilha"])
            & (tabela["regiao"] == serie["regiao"])
            & tabela["valido"]
            & (tabela["periodo"] >= pd.Period(config.PERIODO_INICIO, freq="M"))
            & (tabela["periodo"] <= pd.Period(config.PERIODO_FIM, freq="M"))
        )
        partes.append(tabela[filtro].sort_values("periodo"))
    return pd.concat(partes, ignore_index=True)
