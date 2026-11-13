"""Leitura dos dados originais (data/raw/).

Nenhuma função daqui altera os arquivos em disco: elas apenas leem e devolvem
DataFrames. A limpeza fica em `src.cleaning`.
"""

from pathlib import Path

import pandas as pd

from src import config


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
    conab/feijao/). Deve buscar recursivamente os arquivos .xls/.xlsx
    (ignorando o README.md), para que o notebook 03 saiba quais produtos já
    foram baixados.
    """
    raise NotImplementedError


def carregar_conab(produto: str, diretorio: Path = config.DIR_CONAB) -> pd.DataFrame:
    """Lê a planilha de custo de produção da CONAB de um produto.

    Decisão 5: só faz sentido para os produtos em `config.PRODUTOS_CONAB`
    (Arroz, Feijão, Café, Leite); para outros deve lançar ValueError.

    Deve:
    - localizar o(s) arquivo(s) do produto na subpasta dele em `diretorio`
      (arroz e feijão têm duas planilhas cada; a escolha é feita no notebook 03);
    - ler arquivos .xls com `engine="xlrd"`;
    - ler a planilha e extrair a série de custo (período, região, valor, unidade);
    - devolver um DataFrame "longo" com colunas como: periodo, regiao, custo,
      unidade.

    TODO: o formato real das planilhas ainda é desconhecido. Conforme a
    decisão 5, baixar primeiro só o arquivo do feijão e conferir frequência
    (safra x mês), região e unidade antes de implementar esta função.
    """
    raise NotImplementedError
