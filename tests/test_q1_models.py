"""Testes de src/q1_models.py (parte C).

A maioria das funções ainda é esqueleto (NotImplementedError); os testes
correspondentes ficam marcados como skip até a etapa 4 ser implementada.
"""

import pytest

from src.q1_models import BaselineIngenuo


def test_baseline_ingenuo_usa_lag_1_por_padrao():
    baseline = BaselineIngenuo()
    assert baseline.coluna_preco_atual == "lag_1"


def test_baseline_ingenuo_guarda_a_coluna_configurada():
    baseline = BaselineIngenuo(coluna_preco_atual="lag_2")
    assert baseline.coluna_preco_atual == "lag_2"


@pytest.mark.skip(reason="BaselineIngenuo.fit/predict ainda não implementados (etapa 4)")
def test_baseline_ingenuo_predict_repete_o_preco_atual():
    ...


@pytest.mark.skip(reason="criar_regressao_linear ainda não implementada (etapa 4)")
def test_criar_regressao_linear():
    ...


@pytest.mark.skip(reason="criar_knn ainda não implementada (etapa 4)")
def test_criar_knn():
    ...


@pytest.mark.skip(reason="criar_ensemble só é decidido após os primeiros resultados (decisão 6)")
def test_criar_ensemble():
    ...


@pytest.mark.skip(reason="escolher_hiperparametros ainda não implementada (etapa 4)")
def test_escolher_hiperparametros():
    ...
