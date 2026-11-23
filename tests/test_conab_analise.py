"""Testes da comparação com e sem CONAB e da variação anual."""

import numpy as np
import pandas as pd
import pytest

from src import config
from src.conab_analise import (
    comparar_modelos_com_sem_conab,
    comparar_variacao_anual,
    divisao_por_data,
)


@pytest.fixture(scope="module")
def geral():
    meses = pd.period_range(config.PERIODO_INICIO, periods=config.TOTAL_MESES, freq="M")
    rng = np.random.default_rng(config.SEMENTE)
    return pd.DataFrame({
        "produto": "Arroz",
        "mes": meses,
        "preco": 20 + np.cumsum(rng.normal(0.05, 0.3, config.TOTAL_MESES)),
        "n_mercados": 27,
    })


@pytest.fixture(scope="module")
def conab():
    return pd.DataFrame({
        "produto": "Arroz",
        "periodo": pd.PeriodIndex(["2023-03", "2024-03", "2025-03", "2026-03"], freq="M"),
        "custo": [1.0, 1.1, 1.05, 1.2],
    })


def test_divisao_por_data_nunca_treina_com_o_futuro():
    meses = pd.period_range("2024-01", periods=6, freq="M")
    base = pd.DataFrame({"mes": meses, "lag_1": range(6)}).iloc[1:]

    divisoes = list(divisao_por_data(base, pd.Period("2024-04", freq="M")))

    assert [teste["mes"].iloc[0] for _, teste in divisoes] == list(meses[3:])
    assert all(treino["mes"].max() < teste["mes"].min() for treino, teste in divisoes)


def test_comparacao_usa_mesmos_meses_e_treino(geral, conab):
    tabela = comparar_modelos_com_sem_conab(geral, conab, produtos=["Arroz"])

    assert set(tabela["modelo"]) == {"baseline", "linear", "linear+CONAB", "knn", "knn+CONAB"}
    assert set(tabela["defasagem"]) == set(config.DEFASAGENS_CONAB)
    assert (tabela["n_teste"] == 11).all()
    assert tabela.groupby("defasagem")["n_treino_inicial"].nunique().eq(1).all()


def test_variacao_anual_tem_tres_comparacoes(geral, conab):
    tabela = comparar_variacao_anual(geral, conab, produtos=["Arroz"])

    assert len(tabela) == 3
    assert tabela["var_custo_pct"].iloc[0] == pytest.approx(10.0)
    precos = geral.set_index("mes")["preco"]
    esperado = (precos[pd.Period("2024-03", freq="M")] / precos[pd.Period("2023-03", freq="M")] - 1) * 100
    assert tabela["var_preco_pct"].iloc[0] == pytest.approx(esperado)
