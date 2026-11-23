"""Limpeza da base ICB: tipos, nomes de produto, filtro de produtos e
tratamento de registros inválidos, duplicados, fora da embalagem padrão ou com
preço atípico.

A ordem das etapas está em `limpar_base`. O resultado é salvo em
data/processed/ pelo notebook 01. Decisões: 2 (produtos e nomes) e 10
(critérios de limpeza) em docs/decisoes.md.
"""

import numpy as np
import pandas as pd

from src import config


def converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas para os tipos corretos.

    - COL_MES e COL_DATA_COLETA viram datetime. Se vierem como número serial
      do Excel, são convertidas a partir de 1899-12-30 (a origem do Excel).
    - COL_MES é normalizada para o primeiro dia do mês.
    - Preço, quantidade e PPK viram números (texto inválido vira NaN e é
      removido depois, em `remover_registros_invalidos`).
    - Espaços extras são removidos de Produto, Estab e Marca.
    """
    df = df.copy()

    for coluna in (config.COL_MES, config.COL_DATA_COLETA):
        if pd.api.types.is_numeric_dtype(df[coluna]):
            df[coluna] = pd.to_datetime(df[coluna], unit="D", origin="1899-12-30")
        else:
            df[coluna] = pd.to_datetime(df[coluna], errors="coerce")
    df[config.COL_MES] = df[config.COL_MES].dt.to_period("M").dt.to_timestamp()

    for coluna in (config.COL_PRECO, config.COL_QUANTIDADE, config.COL_PPK):
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    # Só mexe em valores de texto: marcas vazias (NaN) continuam vazias.
    for coluna in (config.COL_PRODUTO, config.COL_MERCADO, config.COL_MARCA):
        df[coluna] = df[coluna].map(lambda v: v.strip() if isinstance(v, str) else v)

    return df


def padronizar_nomes_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica nomes duplicados de produto usando `config.MAPA_NOMES_PRODUTOS`.

    Decisão 2 (limpeza obrigatória de nomes): ex. "Pão" -> "Pão Francês",
    "Farinha" -> "Farinha de Trigo". Nomes fora do mapa ficam inalterados.
    """
    df = df.copy()
    df[config.COL_PRODUTO] = df[config.COL_PRODUTO].replace(config.MAPA_NOMES_PRODUTOS)
    return df


def filtrar_produtos(df: pd.DataFrame, produtos: list[str] | None = None) -> pd.DataFrame:
    """Mantém apenas os produtos analisados (decisão 2; padrão: `config.PRODUTOS`)."""
    produtos = config.PRODUTOS if produtos is None else produtos
    return df[df[config.COL_PRODUTO].isin(produtos)]


def remover_registros_invalidos(df: pd.DataFrame) -> pd.DataFrame:
    """Remove registros que não podem ser usados.

    - sem mês, mercado, produto ou PPK;
    - preço, quantidade ou PPK zero ou negativo.

    A data de coleta e a marca podem faltar: a análise usa o mês, e produtos
    como hortifrúti, carne e pão não têm marca.
    """
    obrigatorias = [config.COL_MES, config.COL_MERCADO, config.COL_PRODUTO, config.COL_PPK]
    df = df.dropna(subset=obrigatorias)
    positivos = (
        (df[config.COL_PRECO] > 0)
        & (df[config.COL_QUANTIDADE] > 0)
        & (df[config.COL_PPK] > 0)
    )
    return df[positivos]


def remover_duplicatas(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas idênticas em todas as colunas, mantendo uma cópia.

    Decisão 10: uma linha igual em mercado, dia, produto, marca, preço e
    quantidade é tratada como a mesma coleta registrada mais de uma vez; sem
    isso, o mesmo preço contaria em dobro na mediana do mercado.
    Linhas da mesma marca com preço ou dia diferente NÃO são removidas.
    """
    return df.drop_duplicates()


def filtrar_embalagem_padrao(
    df: pd.DataFrame,
    embalagens: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Mantém só os registros na embalagem padrão de cada produto.

    Decisão 10: compara sempre o mesmo item (ex.: manteiga em pote de 200 g,
    sem os potes de 250/500 g, muitos deles margarina). Também elimina
    quantidades digitadas erradas (ex.: tomate com quantidade 20).

    Lança ValueError se algum produto da base não tiver embalagem definida em
    `config.EMBALAGEM_PADRAO`, para não descartar um produto inteiro sem aviso.
    """
    embalagens = config.EMBALAGEM_PADRAO if embalagens is None else embalagens
    sem_padrao = set(df[config.COL_PRODUTO].unique()) - set(embalagens)
    if sem_padrao:
        raise ValueError(f"Produtos sem embalagem padrão definida: {sorted(sem_padrao)}")

    padrao = df[config.COL_PRODUTO].map(embalagens).astype(float)
    # isclose em vez de == porque quantidades como 0.2 são números decimais.
    return df[np.isclose(df[config.COL_QUANTIDADE], padrao)]


def remover_precos_atipicos(
    df: pd.DataFrame,
    fator: float = config.FATOR_PRECO_ATIPICO,
) -> pd.DataFrame:
    """Remove preços muito distantes da mediana do produto no mesmo mês.

    Decisão 10: mantém o registro se `mediana / fator <= PPK <= mediana * fator`.
    A comparação é com o MESMO produto e o MESMO mês porque os preços mudam
    com o tempo (inflação, safra). Com fator 3 saem os valores absurdos
    (ex.: banana a R$ 999/kg, pão a R$ 0,10/kg) e também alguns preços de
    hortifrúti perto de 1/3 da mediana que podem ser promoção (limitação
    registrada na decisão 10).
    """
    mediana = df.groupby([config.COL_PRODUTO, config.COL_MES])[config.COL_PPK].transform("median")
    razao = df[config.COL_PPK] / mediana
    return df[(razao <= fator) & (razao >= 1 / fator)]


def limpar_base(
    df: pd.DataFrame,
    produtos: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa a limpeza completa e informa quantas linhas cada etapa removeu.

    Ordem (importa):
    1. `converter_tipos`
    2. `padronizar_nomes_produtos` — antes do filtro, senão "Pão" seria perdido
    3. `filtrar_produtos`
    4. `remover_registros_invalidos`
    5. `remover_duplicatas`
    6. `filtrar_embalagem_padrao`
    7. `remover_precos_atipicos` — por último, para a mediana de referência
       já ser calculada sem duplicatas e sem embalagens diferentes

    Returns:
        (base_limpa, resumo): a base limpa e uma tabela com as linhas
        restantes e removidas em cada etapa (vai para o relatório).
    """
    etapas = [
        ("converter_tipos", converter_tipos),
        ("padronizar_nomes_produtos", padronizar_nomes_produtos),
        ("filtrar_produtos", lambda d: filtrar_produtos(d, produtos)),
        ("remover_registros_invalidos", remover_registros_invalidos),
        ("remover_duplicatas", remover_duplicatas),
        ("filtrar_embalagem_padrao", filtrar_embalagem_padrao),
        ("remover_precos_atipicos", remover_precos_atipicos),
    ]

    linhas = [{"etapa": "base original", "linhas": len(df), "removidas": 0}]
    for nome, funcao in etapas:
        antes = len(df)
        df = funcao(df)
        linhas.append({"etapa": nome, "linhas": len(df), "removidas": antes - len(df)})

    return df.reset_index(drop=True), pd.DataFrame(linhas)
