"""Testes de src/q1_models.py (parte C)."""

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import config
from src.q1_models import (
    BaselineIngenuo,
    EnsemblePonderado,
    criar_ensemble,
    criar_gradient_boosting,
    criar_knn,
    criar_random_forest,
    criar_regressao_linear,
    diagnostico_extrapolacao,
    escolher_hiperparametros,
    escolher_n_lags,
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


def test_criar_ensemble_e_um_ensemble_ponderado_com_pesos():
    submodelos = {
        "baseline": (BaselineIngenuo(), ["lag_1"]),
        "regressao_linear": (criar_regressao_linear(), ["lag_1", "lag_2"]),
        "knn": (criar_knn(k=3), ["lag_1", "lag_2", "lag_3"]),
    }
    pesos = {"baseline": 2.0, "regressao_linear": 1.0, "knn": 0.5}

    ensemble = criar_ensemble(submodelos, pesos)

    assert isinstance(ensemble, EnsemblePonderado)
    nomes = [nome for nome, _, _, _ in ensemble.submodelos]
    colunas = [colunas for _, _, colunas, _ in ensemble.submodelos]
    pesos_guardados = [peso for _, _, _, peso in ensemble.submodelos]
    assert nomes == ["baseline", "regressao_linear", "knn"]
    assert colunas == [["lag_1"], ["lag_1", "lag_2"], ["lag_1", "lag_2", "lag_3"]]
    assert pesos_guardados == [2.0, 1.0, 0.5]


def test_criar_ensemble_preve_a_media_ponderada():
    X = pd.DataFrame({"lag_1": [10.0, 20.0, 30.0, 40.0]})
    y = X["lag_1"] + 1  # relação perfeitamente linear

    submodelos = {
        "baseline": (BaselineIngenuo(), ["lag_1"]),
        "regressao_linear": (criar_regressao_linear(), ["lag_1"]),
    }
    ensemble = criar_ensemble(submodelos, {"baseline": 1.0, "regressao_linear": 1.0}).fit(X, y)

    previsto = ensemble.predict(X)
    erro_ensemble = np.abs(previsto - y.to_numpy()).mean()
    erro_baseline = np.abs(X["lag_1"].to_numpy() - y.to_numpy()).mean()

    # a regressão linear acerta quase perfeitamente aqui; a média com o
    # baseline (que ignora a tendência) deve errar menos que o baseline só.
    assert erro_ensemble < erro_baseline


def test_criar_ensemble_aceita_colunas_diferentes_por_submodelo():
    # Regressão: o EnsemblePonderado existe para permitir que cada submodelo
    # use seu próprio n_lags (pendência 2) — o VotingRegressor não aceitava isso.
    X = pd.DataFrame({
        "lag_1": [10.0, 20.0, 30.0, 40.0],
        "lag_2": [9.0, 10.0, 20.0, 30.0],
        "lag_3": [8.0, 9.0, 10.0, 20.0],
    })
    y = X["lag_1"] + 1

    submodelos = {
        "baseline": (BaselineIngenuo(), ["lag_1"]),
        "knn": (criar_knn(k=1), ["lag_1", "lag_2", "lag_3"]),
    }
    ensemble = criar_ensemble(submodelos, {"baseline": 1.0, "knn": 1.0}).fit(X, y)

    assert ensemble.predict(X).shape == (4,)


def test_escolher_pesos_ensemble_pesa_mais_quem_erra_menos():
    mes = pd.period_range("2020-01", periods=36, freq="M")
    precos = 10 + np.arange(36) * 0.5  # tendência linear perfeita

    geral = pd.DataFrame({
        "produto": ["Cafe"] * 36,
        "mes": mes,
        "preco": precos,
        "n_mercados": 27,
    })

    pesos = escolher_pesos_ensemble(geral, "Cafe", n_lags_linear=1, n_lags_knn=1, k=1)

    assert set(pesos) == {"baseline", "regressao_linear", "knn"}
    # com tendência linear perfeita, a regressão linear deve errar bem menos
    # que o baseline (que ignora a tendência) e por isso pesar mais.
    assert pesos["regressao_linear"] > pesos["baseline"]


def test_criar_random_forest_e_regularizada_para_poucos_meses():
    modelo = criar_random_forest()

    assert isinstance(modelo, RandomForestRegressor)
    assert modelo.max_depth == 4
    assert modelo.min_samples_leaf == 2
    assert modelo.random_state == config.SEMENTE


def test_criar_gradient_boosting_usa_a_mesma_semente():
    modelo = criar_gradient_boosting()

    assert isinstance(modelo, GradientBoostingRegressor)
    assert modelo.random_state == config.SEMENTE


def test_random_forest_aprende_relacao_simples():
    X = pd.DataFrame({"lag_1": np.tile(np.arange(10, dtype=float), 5)})
    y = X["lag_1"] + 1

    modelo = criar_random_forest().fit(X, y)
    previsto = modelo.predict(X)

    assert np.abs(previsto - y.to_numpy()).mean() < 1.0


def test_diagnostico_extrapolacao_detecta_teste_acima_do_treino():
    base = pd.DataFrame({
        "mes": pd.period_range("2020-01", periods=48, freq="M"),
        "alvo": np.arange(48, dtype=float),  # tendência de alta: teste > treino
    })

    diagnostico = diagnostico_extrapolacao(base, primeiro_mes_teste=pd.Period("2023-01", freq="M"))

    assert diagnostico["max_alvo_treino"] == 35.0
    assert diagnostico["max_alvo_teste"] == 47.0
    assert diagnostico["extrapola"]


def test_diagnostico_extrapolacao_nao_marca_serie_estavel():
    base = pd.DataFrame({
        "mes": pd.period_range("2020-01", periods=48, freq="M"),
        "alvo": [10.0] * 48,  # preço constante: teste nunca passa do treino
    })

    diagnostico = diagnostico_extrapolacao(base, primeiro_mes_teste=pd.Period("2023-01", freq="M"))

    assert not diagnostico["extrapola"]


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


def test_escolher_n_lags_devolve_candidato_valido():
    mes = pd.period_range("2020-01", periods=36, freq="M")
    rng = np.random.default_rng(0)
    precos = 10 + np.cumsum(rng.normal(0.1, 0.3, size=36))
    geral = pd.DataFrame({
        "produto": ["Cafe"] * 36,
        "mes": mes,
        "preco": precos,
        "n_mercados": 27,
    })

    resultado = escolher_n_lags(geral, "Cafe", criar_regressao_linear)

    assert resultado["n_lags"] in config.LAGS_CANDIDATOS


def test_escolher_n_lags_usa_criar_modelo_passado_e_nao_so_knn():
    # Regressão: escolher_n_lags precisa criar o modelo a partir do
    # `criar_modelo` recebido (não cair de volta para KNN por engano).
    mes = pd.period_range("2020-01", periods=36, freq="M")
    rng = np.random.default_rng(0)
    precos = 10 + np.cumsum(rng.normal(0.1, 0.3, size=36))
    geral = pd.DataFrame({
        "produto": ["Cafe"] * 36,
        "mes": mes,
        "preco": precos,
        "n_mercados": 27,
    })

    chamadas = []

    def criar_modelo_espiao():
        chamadas.append(1)
        return criar_regressao_linear()

    escolher_n_lags(geral, "Cafe", criar_modelo_espiao)

    assert len(chamadas) > 0
