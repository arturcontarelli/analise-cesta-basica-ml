"""Testes de src/q1_models.py (parte C).

`criar_ensemble` ainda é esqueleto por decisão do projeto (decisão 6: só
implementar depois dos primeiros resultados), por isso continua com skip.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import config
from src.q1_models import (
    BaselineIngenuo,
    criar_knn,
    criar_regressao_linear,
    escolher_hiperparametros,
)


def test_baseline_ingenuo_usa_lag_1_por_padrao():
    baseline = BaselineIngenuo()
    assert baseline.coluna_preco_atual == "lag_1"


def test_baseline_ingenuo_guarda_a_coluna_configurada():
    baseline = BaselineIngenuo(coluna_preco_atual="lag_2")
    assert baseline.coluna_preco_atual == "lag_2"


def test_baseline_ingenuo_predict_repete_o_preco_atual():
    X = pd.DataFrame({"lag_1": [10.0, 11.0, 12.0], "lag_2": [9.0, 10.0, 11.0]})

    baseline = BaselineIngenuo().fit(X)

    assert baseline.predict(X).tolist() == [10.0, 11.0, 12.0]


def test_criar_regressao_linear_e_um_pipeline_com_scaler():
    modelo = criar_regressao_linear()

    assert isinstance(modelo, Pipeline)
    assert isinstance(modelo.named_steps["scaler"], StandardScaler)
    assert isinstance(modelo.named_steps["regressor"], LinearRegression)


def test_criar_regressao_linear_aprende_relacao_simples():
    X = pd.DataFrame({"lag_1": np.arange(20, dtype=float)})
    y = X["lag_1"] + 1  # alvo = preço atual + 1, relação perfeitamente linear

    modelo = criar_regressao_linear().fit(X, y)
    previsto = modelo.predict(X)

    assert previsto[-1] == pytest.approx(y.iloc[-1], abs=0.01)


def test_criar_knn_e_um_pipeline_com_scaler_e_k_vizinhos():
    modelo = criar_knn(k=3)

    assert isinstance(modelo, Pipeline)
    assert isinstance(modelo.named_steps["scaler"], StandardScaler)
    assert modelo.named_steps["regressor"].n_neighbors == 3


@pytest.mark.skip(reason="criar_ensemble só é decidido após os primeiros resultados (decisão 6)")
def test_criar_ensemble():
    ...


def test_escolher_hiperparametros_devolve_candidato_valido():
    mes = pd.period_range("2020-01", periods=36, freq="M")
    rng = np.random.default_rng(0)
    precos = 10 + np.cumsum(rng.normal(0.1, 0.3, size=36))
    geral = pd.DataFrame({
        "produto": ["Cafe"] * 36,
        "mes": mes,
        "preco": precos,
        "n_mercados": 27,
    })

    resultado = escolher_hiperparametros(geral, "Cafe")

    assert resultado["n_lags"] in config.LAGS_CANDIDATOS
    assert resultado["k"] in config.K_VIZINHOS_CANDIDATOS
