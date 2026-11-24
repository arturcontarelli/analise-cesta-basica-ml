"""Divisão temporal e métricas de avaliação da Q1.

Decisão 7: toda avaliação usa DIVISÃO TEMPORAL (treino nos meses mais antigos,
teste nos mais recentes) ou walk-forward. É PROIBIDO usar k-fold embaralhado
(`KFold(shuffle=True)`, `train_test_split` com shuffle etc.): em série temporal
ele faz o modelo treinar com o futuro para prever o passado (vazamento, aula 10,
slide 25).

Todas as funções de divisão abaixo assumem que `base`/`treino` têm uma coluna
`"mes"` e uma linha por mês, já no formato longo da decisão 9.
"""

from collections.abc import Iterator

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
)
from sklearn.model_selection import TimeSeriesSplit

from src import config


def divisao_temporal(
    base: pd.DataFrame,
    meses_treino: int = config.MESES_TREINO,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa a base em treino (primeiros meses) e teste (meses seguintes).

    Decisão 7: ex. treinar até o mês 36 e testar nos meses 37 a 48.
    Deve verificar que a base está em ordem cronológica e que nenhum mês
    do teste é anterior a um mês do treino.
    """
    base = base.sort_values("mes").reset_index(drop=True)
    treino = base.iloc[:meses_treino]
    teste = base.iloc[meses_treino:]
    assert treino["mes"].max() < teste["mes"].min()
    return treino, teste


def divisao_treino_validacao(
    treino: pd.DataFrame,
    meses_validacao: int = config.MESES_VALIDACAO,
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Gera folds de validação dentro do treino, por DATA (não por posição).

    Decisão 7 (aula 10, slide 26) + decisão 2.2 (validação robusta) +
    pendência 2 (`docs/pendencias_parte_c.md`): hiperparâmetros (k do KNN,
    número de lags) e pesos do ensemble são escolhidos pela média do erro
    nesses folds, nunca olhando o teste.

    O corte usa `divisao_por_data`, não a posição da linha: como cada
    candidato de `n_lags` perde uma quantidade diferente de linhas iniciais
    em `features.montar_base_q1`, um corte por posição validaria cada
    candidato (e cada submodelo do ensemble) num período diferente — o mesmo
    problema do item 1, só que na validação em vez do teste final. Como
    `features.montar_base_q1` só descarta a ÚLTIMA linha por falta de alvo
    (a perda de linhas por `n_lags` é sempre no INÍCIO), o mês mais recente de
    `treino` é sempre o mesmo independente de `n_lags`, então cortar pelos
    últimos `meses_validacao` meses (por data) dá o mesmo período de
    validação para qualquer candidato.

    Devolve uma LISTA (não um generator): quem usa isso precisa percorrer os
    mesmos folds mais de uma vez (ex. uma vez por combinação de
    hiperparâmetro candidata), e um generator só pode ser percorrido uma
    única vez.
    """
    meses = sorted(treino["mes"].unique())
    primeiro_mes_validacao = meses[-meses_validacao]
    return list(divisao_por_data(treino, primeiro_mes_validacao))


def walk_forward(
    base: pd.DataFrame,
    meses_treino_inicial: int = config.MESES_TREINO,
) -> Iterator[tuple[pd.DataFrame, pd.DataFrame]]:
    """Gera divisões em janela que avança mês a mês (walk-forward).

    Decisão 7: a cada passo, treina com todos os meses até t e testa no
    mês t+1; depois avança um mês. Deve produzir (treino, teste) com o teste
    sempre de um único mês, posterior a todo o treino.

    Implementação via `TimeSeriesSplit(n_splits=len(base) - meses_treino_inicial,
    test_size=1)`: com `test_size=1`, cada fold de teste é 1 mês; com esse
    `n_splits`, o primeiro fold já começa com exatamente `meses_treino_inicial`
    meses de treino (o resto é o walk-forward natural do sklearn).
    """
    base = base.sort_values("mes").reset_index(drop=True)
    n_splits = len(base) - meses_treino_inicial
    splitter = TimeSeriesSplit(n_splits=n_splits, test_size=1)
    for idx_treino, idx_teste in splitter.split(base):
        yield base.iloc[idx_treino], base.iloc[idx_teste]


def divisao_por_data(
    base: pd.DataFrame,
    primeiro_mes_teste: pd.Period,
) -> Iterator[tuple[pd.DataFrame, pd.DataFrame]]:
    """Gera walk-forward com corte por DATA do mês, e não pela posição da linha.

    Decisão 7 (revisão do item 1 de `docs/pendencias_parte_c.md`): usar aqui
    em vez de `walk_forward` sempre que o resultado for comparado entre
    produtos diferentes. Produtos com `n_lags` maior perdem mais linhas
    iniciais em `features.montar_base_q1`, então um corte por posição (como
    `walk_forward` faz) testaria cada produto num período diferente. Com
    corte por data, todo produto é testado exatamente nos mesmos meses.
    """
    base = base.sort_values("mes").reset_index(drop=True)
    for mes in base.loc[base["mes"] >= primeiro_mes_teste, "mes"]:
        yield base[base["mes"] < mes], base[base["mes"] == mes]


def metricas_regressao(y_real: np.ndarray, y_previsto: np.ndarray) -> dict[str, float]:
    """Calcula o erro em valor: MAE e MSE (aulas 09 e 10).

    Responde "quanto vou gastar?". Deve devolver {"MAE": ..., "MSE": ...}.
    """
    return {
        "MAE": mean_absolute_error(y_real, y_previsto),
        "MSE": mean_squared_error(y_real, y_previsto),
    }


def direcao(preco_atual: np.ndarray, preco_referencia: np.ndarray) -> np.ndarray:
    """Converte preços em direção: 1 = "sobe", 0 = "não sobe".

    Decisão 7: cada previsão vira "sobe / não sobe" comparando com o preço
    atual. Aplicar tanto ao preço real do mês seguinte quanto ao previsto.

    Decisão: igualdade conta como "não sobe" (`>` estrito, não `>=`); sem
    tolerância mínima por enquanto (qualquer aumento conta como "sobe"). Se a
    exploração mostrar muita variação de ruído perto de zero, reavaliar.
    """
    diferenca = np.asarray(preco_atual) - np.asarray(preco_referencia)
    return (diferenca > 0).astype(int)


def metricas_direcao(
    preco_atual: np.ndarray,
    y_real: np.ndarray,
    y_previsto: np.ndarray,
) -> dict:
    """Calcula o acerto de direção (aula 10).

    Usa `direcao` para transformar real e previsto em sobe/não sobe e devolve
    matriz de confusão, acurácia, precisão e revocação. Responde "compro agora
    ou espero?". Reportar separado das métricas em valor (decisão 7).
    """
    direcao_real = direcao(y_real, preco_atual)
    direcao_prevista = direcao(y_previsto, preco_atual)

    return {
        "matriz_confusao": confusion_matrix(direcao_real, direcao_prevista),
        "acuracia": accuracy_score(direcao_real, direcao_prevista),
        "precisao": precision_score(direcao_real, direcao_prevista, zero_division=0),
        "revocacao": recall_score(direcao_real, direcao_prevista, zero_division=0),
    }


def avaliar_modelo(
    modelo,
    base: pd.DataFrame,
    colunas_entrada: list[str],
    coluna_alvo: str,
    primeiro_mes_teste: pd.Period,
) -> pd.DataFrame:
    """Avalia um modelo com walk-forward cortado por DATA e reúne as métricas.

    `primeiro_mes_teste` (ver `divisao_por_data`) garante que todo produto é
    testado nos mesmos meses, independente de quantas linhas `n_lags` consumiu
    no início da série do produto.

    Deve treinar e prever respeitando a ordem do tempo, e devolver uma tabela
    com MAE, MSE e as métricas de direção, pronta para comparar com o baseline
    e salvar em reports/tables/.
    """
    y_reais = []
    y_previstos = []
    precos_atuais = []

    for treino_fold, teste_fold in divisao_por_data(base, primeiro_mes_teste):
        modelo.fit(treino_fold[colunas_entrada], treino_fold[coluna_alvo])
        previsto = modelo.predict(teste_fold[colunas_entrada])

        y_reais.append(teste_fold[coluna_alvo].iloc[0])
        y_previstos.append(previsto[0])
        precos_atuais.append(teste_fold["lag_1"].iloc[0])

    y_reais = np.array(y_reais)
    y_previstos = np.array(y_previstos)
    precos_atuais = np.array(precos_atuais)

    metricas = metricas_regressao(y_reais, y_previstos)
    metricas.update(metricas_direcao(precos_atuais, y_reais, y_previstos))

    return pd.DataFrame([metricas])