"""Agregação da base limpa em séries mensais.

- Q1 usa a série GERAL (mediana entre mercados) — decisão 3.
- Q3 usa séries POR MERCADO, só de mercados com série quase completa — decisão 4.

As tabelas devolvidas estão no formato LONGO (decisão 9), com a coluna `mes`
como período mensal (`pd.Period`, freq "M").
"""

import pandas as pd

from src import config


def series_por_mercado(df: pd.DataFrame, mercados: list[str] | None = None) -> pd.DataFrame:
    """Calcula o preço de cada produto em cada mercado e mês.

    É a 1ª etapa da mediana em 2 etapas (decisão 10) e também a série da Q3.
    Se o mercado tem vários registros do produto no mês (várias marcas ou
    visitas), o preço do mercado é a MEDIANA deles.

    Args:
        df: base limpa (saída de `cleaning.limpar_base`).
        mercados: se informado, mantém só esses mercados (normalmente a saída
            de `selecionar_mercados`).

    Returns:
        Tabela longa com colunas `produto`, `mes`, `mercado`, `preco` e
        `n_registros` (quantos registros entraram na mediana do mercado).
    """
    if mercados is not None:
        df = df[df[config.COL_MERCADO].isin(mercados)]

    return (
        df.assign(mes=df[config.COL_MES].dt.to_period("M"))
        .groupby([config.COL_PRODUTO, "mes", config.COL_MERCADO])[config.COL_PPK]
        .agg(preco="median", n_registros="size")
        .reset_index()
        .rename(columns={config.COL_PRODUTO: "produto", config.COL_MERCADO: "mercado"})
        .sort_values(["produto", "mes", "mercado"])
        .reset_index(drop=True)
    )


def serie_geral(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula o preço geral por produto e mês (série usada na Q1).

    Decisão 3 + decisão 10 (mediana em 2 etapas):
    1. mediana de cada mercado no mês (`series_por_mercado`);
    2. mediana ENTRE os mercados.
    Assim cada mercado vale um voto, tenha ele 1 ou 8 marcas do produto.

    Todos os meses entre o primeiro e o último da base aparecem para todos os
    produtos. Um mês sem nenhuma coleta fica com `preco` NaN e `n_mercados` 0
    (não é preenchido aqui): sem isso, os lags da Q1 pulariam o buraco e
    tratariam meses distantes como consecutivos.

    Returns:
        Tabela longa (decisão 9) com colunas `produto`, `mes`, `preco` e
        `n_mercados`, ordenada por produto e mês.
    """
    por_mercado = series_por_mercado(df)
    geral = (
        por_mercado.groupby(["produto", "mes"])["preco"]
        .agg(preco="median", n_mercados="size")
    )

    meses = pd.period_range(por_mercado["mes"].min(), por_mercado["mes"].max(), freq="M")
    grade = pd.MultiIndex.from_product(
        [sorted(por_mercado["produto"].unique()), meses], names=["produto", "mes"]
    )
    geral = geral.reindex(grade)
    geral["n_mercados"] = geral["n_mercados"].fillna(0).astype(int)
    return geral.reset_index()


def meses_por_mercado(df: pd.DataFrame) -> pd.Series:
    """Conta em quantos meses distintos cada mercado foi coletado.

    Usado no notebook 02 para justificar `config.MIN_MESES_MERCADO`
    (decisão 4: gráfico de meses disponíveis por mercado).

    Returns:
        Série indexada pelo mercado, com o número de meses, do maior para o menor.
    """
    return (
        df.groupby(config.COL_MERCADO)[config.COL_MES]
        .nunique()
        .rename("meses")
        .sort_values(ascending=False)
    )


def selecionar_mercados(df: pd.DataFrame, min_meses: int = config.MIN_MESES_MERCADO) -> list[str]:
    """Devolve os mercados com pelo menos `min_meses` meses de coleta.

    Decisão 4: a Q3 usa apenas mercados com série quase completa.
    """
    meses = meses_por_mercado(df)
    return sorted(meses[meses >= min_meses].index)


def preco_relativo(series_mercado: pd.DataFrame, geral: pd.DataFrame) -> pd.DataFrame:
    """Calcula o preço relativo de cada mercado em relação ao preço geral.

    Decisão 4: cada mercado é representado pelo seu preço relativo em cada
    produto (acima ou abaixo da mediana geral). Ex.: razão
    preco_mercado / preco_geral do mesmo produto e mês (1,10 = 10% mais caro).

    TODO: definir na etapa 05 se usar razão ou diferença percentual, e como
    tratar meses em que o mercado não tem o produto.
    """
    raise NotImplementedError
