"""Modelos da Q1: prever o preço do mês seguinte de cada produto.

Decisão 6 — modelos das aulas (obrigatórios):
- baseline ingênuo (régua: o preço do mês seguinte é igual ao atual);
- regressão linear (aula 09);
- KNN regressor (aula 08);
- ensemble (aula 10): média PONDERADA dos três acima (ver `criar_ensemble`).

Modelo extra (decisão 6, decidido após os primeiros resultados: nem o
ensemble bateu o baseline com folga): Random Forest (`criar_random_forest`),
porque bagging de árvores foi citado na aula 10 e captura relação não-linear
entre o custo do produtor e o preço, que a regressão linear não pega.
Gradient Boosting (`criar_gradient_boosting`) entra só como comparação
informal — não foi dado na aula e não é o modelo extra oficial da decisão 6.

Todos os modelos devem seguir a interface do scikit-learn (fit/predict), para
serem avaliados da mesma forma em `src.evaluation`.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import config, evaluation, features

# Evita divisão por zero em `escolher_pesos_ensemble` quando um modelo acerta
# a validação perfeitamente (MAE = 0).
EPSILON_PESO = 1e-6


class BaselineIngenuo(RegressorMixin, BaseEstimator):
    """Baseline ingênuo: prevê que o preço do mês seguinte é igual ao atual.

    Decisão 6: serve de régua. Se um modelo não erra menos que isso, ele não
    aprendeu nada útil.

    `RegressorMixin` precisa vir ANTES de `BaseEstimator` na herança: a partir
    do scikit-learn 1.6, `is_regressor()` usa o sistema de tags
    (`__sklearn_tags__`), e a ordem errada faz o MRO usar os tags genéricos de
    `BaseEstimator` em vez dos de `RegressorMixin`. O ensemble (`EnsemblePonderado`)
    não depende mais disso — ele chama `fit`/`predict` direto, sem passar por
    `VotingRegressor` —, mas a ordem certa ainda é convenção do scikit-learn e
    evita surpresa se este modelo for usado em outra ferramenta da biblioteca
    (ex.: `cross_val_score`, `GridSearchCV`) que confira a tag.

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


def criar_random_forest() -> RandomForestRegressor:
    """Cria a Random Forest (modelo extra, decisão 6).

    Hiperparâmetros fixos (não escolhidos por validação, ao contrário do
    `k` do KNN): `max_depth` e `min_samples_leaf` pequenos para não decorar
    o treino, já que cada produto tem só ~30 meses de treino.

    Limitação conhecida: árvores não extrapolam além do intervalo de preço
    visto no treino. Numa série com tendência de alta, meses de teste com
    preço recorde tendem a ser subestimados por esse motivo estrutural, não
    por falta de padrão nos dados — ver `diagnostico_extrapolacao`.
    """
    return RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        min_samples_leaf=2,
        random_state=config.SEMENTE,
    )


def criar_gradient_boosting() -> GradientBoostingRegressor:
    """Cria o Gradient Boosting só para comparação informal com a Random Forest.

    NÃO é modelo "das aulas" (só bagging foi dado, não boosting) nem o modelo
    extra oficial da decisão 6 — serve só para checar se boosting supera a
    Random Forest nesses dados. Sofre da mesma limitação de extrapolação por
    ser baseado em árvores (ver `criar_random_forest`).
    """
    return GradientBoostingRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        min_samples_leaf=2,
        random_state=config.SEMENTE,
    )


def diagnostico_extrapolacao(base: pd.DataFrame, meses_treino: int = config.MESES_TREINO) -> dict:
    """Indica se o teste tem preços fora do intervalo visto no treino.

    Random Forest e Gradient Boosting não extrapolam (decisão 6): se o
    alvo máximo do teste for maior que o do treino, esses modelos tendem a
    subestimar esses meses por limitação estrutural das árvores, não por
    falta de padrão nos dados.
    """
    treino, teste = evaluation.divisao_temporal(base, meses_treino)
    return {
        "max_alvo_treino": treino["alvo"].max(),
        "max_alvo_teste": teste["alvo"].max(),
        "extrapola": teste["alvo"].max() > treino["alvo"].max(),
    }


class EnsemblePonderado(RegressorMixin, BaseEstimator):
    """Ensemble como média PONDERADA (decisão 6), com um conjunto de colunas
    de entrada próprio por submodelo.

    Substitui o `VotingRegressor`: ele exige uma única matriz `X`
    compartilhada entre todos os submodelos, o que obrigava baseline,
    regressão linear e KNN a usar sempre o mesmo `n_lags` (pendência 2 —
    `docs/pendencias_parte_c.md`). Aqui cada submodelo é
    `(nome, modelo, colunas, peso)`, então cada um pode ser validado e usar
    seu próprio `n_lags`, e o `X` passado a `fit`/`predict` só precisa conter
    a união das colunas de todos os submodelos.
    """

    def __init__(self, submodelos: list[tuple[str, BaseEstimator, list[str], float]]):
        self.submodelos = submodelos

    def fit(self, X, y):
        self.ajustados_ = [
            (clone(modelo).fit(X[colunas], y), colunas, peso)
            for _, modelo, colunas, peso in self.submodelos
        ]
        return self

    def predict(self, X) -> np.ndarray:
        previsoes = np.array([modelo.predict(X[colunas]) for modelo, colunas, _ in self.ajustados_])
        pesos = np.array([peso for _, _, peso in self.ajustados_])
        return np.average(previsoes, axis=0, weights=pesos)


def criar_ensemble(submodelos: dict[str, tuple[BaseEstimator, list[str]]], pesos: dict[str, float]) -> EnsemblePonderado:
    """Cria o ensemble (aula 10) como média PONDERADA dos modelos.

    Decisão 6: optou-se por média ponderada em vez de stacking. Nos primeiros
    resultados com dado real, o baseline costuma errar menos que a regressão
    linear e o KNN (ver `docs/previsao_q1.md`) — uma média simples diluiria o
    modelo melhor com os piores, e um stacking exigiria um meta-modelo
    treinado com poucos meses por produto (risco de instabilidade maior do
    que o ganho esperado).

    `submodelos` mapeia nome -> (modelo, colunas de entrada desse modelo).
    Os pesos vêm de `escolher_pesos_ensemble` (inverso do MAE de validação),
    calculados sem olhar o teste (decisão 7).
    """
    nomes = list(submodelos.keys())
    return EnsemblePonderado([
        (nome, submodelos[nome][0], submodelos[nome][1], pesos[nome]) for nome in nomes
    ])


def escolher_pesos_ensemble(base_treino, produto: str, n_lags: int, k: int) -> dict[str, float]:
    """Calcula os pesos do ensemble pelo inverso do erro de validação.

    Usa os mesmos folds de validação de `escolher_hiperparametros`
    (walk-forward dentro do treino, decisão 7), agora medindo o MAE de
    baseline, regressão linear e KNN já com `n_lags`/`k` escolhidos. Peso de
    cada modelo = 1 / (MAE médio de validação + `EPSILON_PESO`): quem erra
    menos pesa mais; o epsilon evita divisão por zero se algum modelo acertar
    a validação perfeitamente.

    `EnsemblePonderado` já faz a média ponderada (via `np.average`) a partir
    dos pesos brutos, por isso não é preciso normalizar para somar 1 aqui.
    """
    base = features.montar_base_q1(base_treino, produto, n_lags)
    folds = evaluation.divisao_treino_validacao(base, config.MESES_VALIDACAO)
    colunas_entrada = [f"lag_{i}" for i in range(1, n_lags + 1)]

    candidatos = {
        "baseline": BaselineIngenuo(),
        "regressao_linear": criar_regressao_linear(),
        "knn": criar_knn(k),
    }

    pesos = {}
    for nome, modelo_base in candidatos.items():
        erros = []
        for treino_fold, validacao_fold in folds:
            modelo = clone(modelo_base)
            modelo.fit(treino_fold[colunas_entrada], treino_fold["alvo"])
            previsto = modelo.predict(validacao_fold[colunas_entrada])
            erros.append(evaluation.metricas_regressao(validacao_fold["alvo"], previsto)["MAE"])
        pesos[nome] = 1 / (sum(erros) / len(erros) + EPSILON_PESO)

    return pesos


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
