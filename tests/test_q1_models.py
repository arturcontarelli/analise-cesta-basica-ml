"""Testes de src/q1_models.py (parte C)."""

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import VotingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import config
from src.q1_models import (
    BaselineIngenuo,
    criar_ensemble,
    criar_knn,
    criar_regressao_linear,
    escolher_hiperparametros,
    escolher_pesos_ensemble,
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


def test_criar_ensemble_e_um_voting_regressor_com_pesos():
    modelos = {
        "baseline": BaselineIngenuo(),
        "regressao_linear": criar_regressao_linear(),
        "knn": criar_knn(k=3),
    }
    pesos = {"baseline": 2.0, "regressao_linear": 1.0, "knn": 0.5}

    ensemble = criar_ensemble(modelos, pesos)

    assert isinstance(ensemble, VotingRegressor)
    assert [nome for nome, _ in ensemble.estimators] == ["baseline", "regressao_linear", "knn"]
    assert ensemble.weights == [2.0, 1.0, 0.5]


def test_criar_ensemble_preve_a_media_ponderada():
    X = pd.DataFrame({"lag_1": [10.0, 20.0, 30.0, 40.0]})
    y = X["lag_1"] + 1  # relação perfeitamente linear

    modelos = {"baseline": BaselineIngenuo(), "regressao_linear": criar_regressao_linear()}
    ensemble = criar_ensemble(modelos, {"baseline": 1.0, "regressao_linear": 1.0}).fit(X, y)

    previsto = ensemble.predict(X)
    erro_ensemble = np.abs(previsto - y.to_numpy()).mean()
    erro_baseline = np.abs(X["lag_1"].to_numpy() - y.to_numpy()).mean()

    # a regressão linear acerta quase perfeitamente aqui; a média com o
    # baseline (que ignora a tendência) deve errar menos que o baseline só.
    assert erro_ensemble < erro_baseline


def test_escolher_pesos_ensemble_pesa_mais_quem_erra_menos():
    mes = pd.period_range("2020-01", periods=36, freq="M")
    precos = 10 + np.arange(36) * 0.5  # tendência linear perfeita

    geral = pd.DataFrame({
        "produto": ["Cafe"] * 36,
        "mes": mes,
        "preco": precos,
        "n_mercados": 27,
    })

    pesos = escolher_pesos_ensemble(geral, "Cafe", n_lags=1, k=1)

    assert set(pesos) == {"baseline", "regressao_linear", "knn"}
    # com tendência linear perfeita, a regressão linear deve errar bem menos
    # que o baseline (que ignora a tendência) e por isso pesar mais.
    assert pesos["regressao_linear"] > pesos["baseline"]


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
