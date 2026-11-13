"""Agregação da base limpa em séries mensais.

- Q1 usa a série GERAL (mediana entre mercados) — decisão 3.
- Q3 usa séries POR MERCADO, só de mercados com série quase completa — decisão 4.
"""

import pandas as pd

from src import config


def serie_geral(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula o preço geral por produto e mês (série usada na Q1).

    Decisão 3: para cada (produto, mês), o preço é a MEDIANA do PPK
    (`config.ESTATISTICA_PRECO_GERAL`) entre todos os mercados coletados
    naquele mês.

    Deve devolver uma tabela com meses nas linhas e produtos nas colunas
    (ou formato longo produto/mês/preço), incluindo também quantos mercados
    entraram em cada mediana, para mostrar na exploração.

    Meses sem nenhuma coleta de um produto devem aparecer como NaN (não
    preencher aqui).
    """
    raise NotImplementedError


def meses_por_mercado(df: pd.DataFrame) -> pd.Series:
    """Conta em quantos meses distintos cada mercado foi coletado.

    Usado no notebook 02 para justificar `config.MIN_MESES_MERCADO`
    (decisão 4: gráfico de meses disponíveis por mercado).
    """
    raise NotImplementedError


def selecionar_mercados(df: pd.DataFrame, min_meses: int = config.MIN_MESES_MERCADO) -> list[str]:
    """Devolve os mercados com pelo menos `min_meses` meses de coleta.

    Decisão 4: a Q3 usa apenas mercados com série quase completa
    (~40 dos 48 meses ou mais, o que dá ~25 dos 51 mercados).
    """
    raise NotImplementedError


def series_por_mercado(df: pd.DataFrame, mercados: list[str] | None = None) -> pd.DataFrame:
    """Calcula o preço de cada produto em cada mercado e mês (série da Q3).

    Deve agregar o PPK por (mercado, produto, mês) — se houver mais de uma
    coleta no mesmo mês, usar a mediana — e filtrar para `mercados`, quando
    informado (normalmente o resultado de `selecionar_mercados`).
    """
    raise NotImplementedError


def preco_relativo(series_mercado: pd.DataFrame, geral: pd.DataFrame) -> pd.DataFrame:
    """Calcula o preço relativo de cada mercado em relação ao preço geral.

    Decisão 4: cada mercado é representado pelo seu preço relativo em cada
    produto (acima ou abaixo da mediana geral). Ex.: razão
    preco_mercado / preco_geral do mesmo produto e mês (1,10 = 10% mais caro).

    TODO: definir na etapa 05 se usar razão ou diferença percentual, e como
    tratar meses em que o mercado não tem o produto.
    """
    raise NotImplementedError
