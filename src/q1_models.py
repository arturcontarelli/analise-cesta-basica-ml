"""Modelos da Q1: prever o preço do mês seguinte de cada produto.

Decisão 6 — modelos das aulas (obrigatórios):
- baseline ingênuo (régua: o preço do mês seguinte é igual ao atual);
- regressão linear (aula 09);
- KNN regressor (aula 08);
- ensemble (aula 10).

Modelo extra (provavelmente Random Forest): a decidir DEPOIS dos primeiros
resultados (decisão 6). Não implementar antes disso.

Todos os modelos devem seguir a interface do scikit-learn (fit/predict), para
serem avaliados da mesma forma em `src.evaluation`.
"""

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import config, evaluation, features


class BaselineIngenuo(BaseEstimator, RegressorMixin):
    """Baseline ingênuo: prevê que o preço do mês seguinte é igual ao atual.

    Decisão 6: serve de régua. Se um modelo não erra menos que isso, ele não
    aprendeu nada útil.

    `predict` deve devolver a coluna do preço atual (`lag_1`, gerada em
    `features.criar_lags`). `fit` não aprende nada, só guarda o índice dessa
    coluna.
    """

    def __init__(self, coluna_preco_atual: str = "lag_1"):
        self.coluna_preco_atual = coluna_preco_atual

    def fit(self, X, y=None):
        self.indice_coluna_ = list(X.columns).index(self.coluna_preco_atual)
        return self

    def predict(self, X) -> np.ndarray:
        if hasattr(X, "columns"):
            return X[self.coluna_preco_atual].to_numpy()
        return np.asarray(X)[:, self.indice_coluna_]


def criar_regressao_linear():
    """Cria o modelo de regressão linear (aula 09) usando os lags como entrada.

    Deve devolver um `sklearn.linear_model.LinearRegression` (ou pipeline com
    padronização, se o grupo decidir).
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression()),
    ])


def criar_knn(k: int):
    """Cria o KNN regressor (aula 08) com `k` vizinhos.

    Deve devolver um pipeline com padronização (StandardScaler) +
    `KNeighborsRegressor`, pois o KNN depende de distâncias.
    O `k` é escolhido em `escolher_hiperparametros`, nunca no teste.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", KNeighborsRegressor(n_neighbors=k)),
    ])


def criar_ensemble(modelos: list):
    """Cria o ensemble (aula 10) combinando os modelos acima.

    Decisão 6: média (ex.: `VotingRegressor`) ou stacking. Atenção: se usar
    stacking, a validação interna do `StackingRegressor` não pode ser k-fold
    embaralhado (decisão 7) — usar `TimeSeriesSplit`.

    TODO: decidir entre média e stacking na etapa 04.
    """
    raise NotImplementedError


def escolher_hiperparametros(base_treino, produto: str) -> dict:
    """Escolhe número de lags e k do KNN usando só treino + validação.

    Decisão 7 (aula 10, slide 26): testar `config.LAGS_CANDIDATOS` e
    `config.K_VIZINHOS_CANDIDATOS` na parte de validação
    (`evaluation.divisao_treino_validacao`) e devolver a melhor combinação
    pelo MAE. Nunca olhar o teste.
    """
    melhor = None

    for n_lags in config.LAGS_CANDIDATOS:
        base = features.montar_base_q1(base_treino, produto, n_lags)
        folds = evaluation.divisao_treino_validacao(base, config.MESES_VALIDACAO)
        colunas_entrada = [f"lag_{i}" for i in range(1, n_lags + 1)]

        for k in config.K_VIZINHOS_CANDIDATOS:
            erros = []
            for treino_fold, validacao_fold in folds:
                modelo = criar_knn(k)
                modelo.fit(treino_fold[colunas_entrada], treino_fold["alvo"])
                previsto = modelo.predict(validacao_fold[colunas_entrada])
                mae = evaluation.metricas_regressao(validacao_fold["alvo"], previsto)["MAE"]
                erros.append(mae)

            mae_medio = sum(erros) / len(erros)
            if melhor is None or mae_medio < melhor["mae"]:
                melhor = {"n_lags": n_lags, "k": k, "mae": mae_medio}

    return {"n_lags": melhor["n_lags"], "k": melhor["k"]}
