"""Testes de src/evaluation.py (parte C).

Usa uma base fictícia no formato longo da decisão 9 (coluna `mes`), para não
depender da base real.
"""

import numpy as np
import pandas as pd
import pytest

from src.evaluation import (
    avaliar_modelo,
    direcao,
    divisao_temporal,
    divisao_treino_validacao,
    metricas_direcao,
    metricas_regressao,
    walk_forward,
)
from src.q1_models import BaselineIngenuo


def _base_exemplo(n_meses: int = 10) -> pd.DataFrame:
    mes = pd.period_range("2024-01", periods=n_meses, freq="M")
    return pd.DataFrame({"mes": mes, "preco": range(n_meses)})


def test_divisao_temporal_respeita_ordem_cronologica():
    base = _base_exemplo(10)
    treino, teste = divisao_temporal(base, meses_treino=7)

    assert len(treino) == 7
    assert len(teste) == 3
    assert treino["mes"].max() < teste["mes"].min()


def test_walk_forward_gera_um_mes_de_teste_por_fold():
    base = _base_exemplo(10)
    folds = list(walk_forward(base, meses_treino_inicial=7))

    assert len(folds) == 3  # 10 meses - 7 de treino inicial
    for treino_fold, teste_fold in folds:
        assert len(teste_fold) == 1
        assert treino_fold["mes"].max() < teste_fold["mes"].min()


def test_walk_forward_janela_de_treino_expande_a_cada_fold():
    base = _base_exemplo(10)
    folds = list(walk_forward(base, meses_treino_inicial=7))

    tamanhos_treino = [len(treino_fold) for treino_fold, _ in folds]
    assert tamanhos_treino == [7, 8, 9]


def test_divisao_treino_validacao_devolve_lista_nao_generator():
    base = _base_exemplo(10)
    folds = divisao_treino_validacao(base, meses_validacao=3)

    assert isinstance(folds, list)


def test_divisao_treino_validacao_pode_ser_percorrida_mais_de_uma_vez():
    # Regressão: já existiu um bug em que isso devolvia um generator e a
    # segunda passada vinha vazia (ver histórico do projeto).
    base = _base_exemplo(10)
    folds = divisao_treino_validacao(base, meses_validacao=3)

    primeira_passada = list(folds)
    segunda_passada = list(folds)

    assert len(primeira_passada) == 3
    assert len(segunda_passada) == len(primeira_passada)


def test_metricas_regressao_calcula_mae_e_mse_sem_trocar():
    y_real = np.array([10, 20, 30])
    y_previsto = np.array([12, 18, 33])

    metricas = metricas_regressao(y_real, y_previsto)

    assert set(metricas.keys()) == {"MAE", "MSE"}
    assert metricas["MAE"] == pytest.approx(7 / 3)
    assert metricas["MSE"] == pytest.approx(17 / 3)


def test_direcao_sobe_quando_maior_que_referencia():
    preco_atual = np.array([11, 10, 10])
    preco_referencia = np.array([10, 10, 11])

    assert direcao(preco_atual, preco_referencia).tolist() == [1, 0, 0]


def test_metricas_direcao_calcula_matriz_e_scores():
    preco_atual = np.array([10, 10, 10, 10])
    y_real = np.array([11, 9, 12, 10])  # sobe, não sobe, sobe, não sobe
    y_previsto = np.array([11, 11, 9, 10])  # sobe, sobe, não sobe, não sobe

    metricas = metricas_direcao(preco_atual, y_real, y_previsto)

    assert set(metricas.keys()) == {"matriz_confusao", "acuracia", "precisao", "revocacao"}
    assert metricas["acuracia"] == pytest.approx(0.5)


def test_avaliar_modelo_com_baseline():
    # alvo = lag_1 + 1 sempre: o baseline (que prevê lag_1) erra exatamente
    # 1 em todo mês, e nunca prevê "sobe" (porque sempre repete o preço atual).
    n = 40
    base = pd.DataFrame({
        "mes": pd.period_range("2020-01", periods=n, freq="M"),
        "lag_1": np.arange(n, dtype=float),
        "lag_2": np.arange(-1, n - 1, dtype=float),
        "alvo": np.arange(1, n + 1, dtype=float),
    })

    resultado = avaliar_modelo(BaselineIngenuo(), base, ["lag_1", "lag_2"], "alvo")

    assert set(resultado.columns) == {
        "MAE", "MSE", "matriz_confusao", "acuracia", "precisao", "revocacao",
    }
    assert resultado["MAE"].iloc[0] == pytest.approx(1.0)
    assert resultado["acuracia"].iloc[0] == pytest.approx(0.0)
