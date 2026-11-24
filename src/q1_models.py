"""Modelos da Q1: prever o preço do mês seguinte de cada produto.

Decisão 6 — modelos das aulas (obrigatórios):
- baseline ingênuo (régua: o preço do mês seguinte é igual ao atual);
- regressão linear (aula 09);
- KNN regressor (aula 08);
- ensemble (aula 10): média PONDERADA dos três acima (ver `criar_ensemble`).

Modelo extra (decisão 6, decidido após os primeiros resultados: nem o
ensemble bateu o baseline com folga): Random Forest (`criar_random_forest`),
porque bagging de árvores foi citado na aula 10 e, diferente dos modelos das
aulas, consegue captar relações entre os lags e o preço que não sejam uma
linha reta. Gradient Boosting (`criar_gradient_boosting`) entra só como
comparação informal — não foi dado na aula e não é o modelo extra oficial da
decisão 6.

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


def diagnostico_extrapolacao(base: pd.DataFrame, primeiro_mes_teste: pd.Period) -> dict:
    """Indica se o teste tem preços fora do intervalo visto no treino.

    Random Forest e Gradient Boosting não extrapolam (decisão 6): se o
    alvo máximo do teste for maior que o do treino, esses modelos tendem a
    subestimar esses meses por limitação estrutural das árvores, não por
    falta de padrão nos dados.

    Corte por DATA, não por posição (decisão 7, atualização — pendência 1):
    `primeiro_mes_teste` deve ser o mesmo usado em `evaluation.avaliar_modelo`,
    para que o treino/teste aqui correspondam exatamente ao período avaliado
    (a posição variaria com `n_lags`, que agora é próprio de cada modelo —
    pendência 2).
    """
    treino = base[base["mes"] < primeiro_mes_teste]
    teste = base[base["mes"] >= primeiro_mes_teste]
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


def escolher_pesos_ensemble(
    base_treino,
    produto: str,
    n_lags_linear: int,
    n_lags_knn: int,
    k: int,
) -> dict[str, float]:
    """Calcula os pesos do ensemble pelo inverso do erro de validação.

    Cada submodelo é validado com o seu próprio `n_lags` (pendência 2 —
    `docs/pendencias_parte_c.md`): a regressão linear usa `n_lags_linear`
    (escolhido em `escolher_n_lags`) e o KNN usa `n_lags_knn`/`k` (escolhidos
    juntos em `escolher_hiperparametros`). O baseline só olha `lag_1`, que
    existe em qualquer uma das duas bases — usa-se a do KNN por conveniência.
    Como `evaluation.divisao_treino_validacao` corta por data, os três são
    comparados no mesmo período de validação mesmo com `n_lags` diferentes.

    Peso de cada modelo = 1 / (MAE médio de validação + `EPSILON_PESO`):
    quem erra menos pesa mais; o epsilon evita divisão por zero se algum
    modelo acertar a validação perfeitamente.

    `EnsemblePonderado` já faz a média ponderada (via `np.average`) a partir
    dos pesos brutos, por isso não é preciso normalizar para somar 1 aqui.
    """
    base_linear = features.montar_base_q1(base_treino, produto, n_lags_linear)
    base_knn = features.montar_base_q1(base_treino, produto, n_lags_knn)

    candidatos = {
        "baseline": (BaselineIngenuo(), base_knn, ["lag_1"]),
        "regressao_linear": (criar_regressao_linear(), base_linear, [f"lag_{i}" for i in range(1, n_lags_linear + 1)]),
        "knn": (criar_knn(k), base_knn, [f"lag_{i}" for i in range(1, n_lags_knn + 1)]),
    }

    pesos = {}
    for nome, (modelo_base, base, colunas_entrada) in candidatos.items():
        folds = evaluation.divisao_treino_validacao(base, config.MESES_VALIDACAO)
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


def escolher_n_lags(base_treino, produto: str, criar_modelo) -> dict:
    """Escolhe o número de lags que minimiza o erro de validação de um modelo
    sem hiperparâmetro próprio (regressão linear, Random Forest, Gradient
    Boosting).

    Generaliza `escolher_hiperparametros` (que busca `n_lags` e `k` juntos,
    só para o KNN) para dar a cada modelo seu próprio `n_lags` — pendência 2
    (`docs/pendencias_parte_c.md`): o melhor `n_lags` para o KNN não é
    necessariamente o melhor para os outros modelos.

    `criar_modelo` é uma função sem argumentos que devolve uma instância nova
    do modelo (ex. `criar_regressao_linear`, `criar_random_forest`). Nunca
    olha o teste (decisão 7).
    """
    melhor = None

    for n_lags in config.LAGS_CANDIDATOS:
        base = features.montar_base_q1(base_treino, produto, n_lags)
        folds = evaluation.divisao_treino_validacao(base, config.MESES_VALIDACAO)
        colunas_entrada = [f"lag_{i}" for i in range(1, n_lags + 1)]

        erros = []
        for treino_fold, validacao_fold in folds:
            modelo = criar_modelo()
            modelo.fit(treino_fold[colunas_entrada], treino_fold["alvo"])
            previsto = modelo.predict(validacao_fold[colunas_entrada])
            erros.append(evaluation.metricas_regressao(validacao_fold["alvo"], previsto)["MAE"])

        mae_medio = sum(erros) / len(erros)
        if melhor is None or mae_medio < melhor["mae"]:
            melhor = {"n_lags": n_lags, "mae": mae_medio}

    return {"n_lags": melhor["n_lags"]}
