"""Testes de src/features.py (parte C).

Usa séries fictícias pequenas, no formato combinado com a parte A (decisão 9),
para não depender da base real.
"""

import numpy as np
import pandas as pd
import pytest

from src.features import criar_alvo, criar_lags


def _serie_exemplo() -> pd.Series:
    indice = pd.period_range("2024-01", periods=5, freq="M")
    return pd.Series([10, 11, 12, 13, 14], index=indice, dtype=float)


def test_criar_lags_lag1_e_o_preco_atual():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=2)

    assert lags["lag_1"].tolist() == serie.tolist()


def test_criar_lags_lag2_e_o_mes_anterior():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=2)

    assert np.isnan(lags["lag_2"].iloc[0])
    assert lags["lag_2"].iloc[1:].tolist() == serie.iloc[:-1].tolist()


def test_criar_lags_gera_n_colunas_do_tamanho_da_serie():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=3)

    assert list(lags.columns) == ["lag_1", "lag_2", "lag_3"]
    assert len(lags) == len(serie)


def test_criar_alvo_e_o_preco_do_mes_seguinte():
    serie = _serie_exemplo()
    alvo = criar_alvo(serie)

    assert alvo.name == "alvo"
    assert alvo.iloc[:-1].tolist() == serie.iloc[1:].tolist()
    assert np.isnan(alvo.iloc[-1])


@pytest.mark.skip(reason="adicionar_variaveis_conab ainda não implementada (etapa 7, aguarda a parte B)")
def test_adicionar_variaveis_conab():
    ...


@pytest.mark.skip(reason="montar_base_q1 ainda não implementada")
def test_montar_base_q1():
    ...
