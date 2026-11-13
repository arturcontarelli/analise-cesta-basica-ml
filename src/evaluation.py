"""Divisão temporal e métricas de avaliação da Q1.

Decisão 7: toda avaliação usa DIVISÃO TEMPORAL (treino nos meses mais antigos,
teste nos mais recentes) ou walk-forward. É PROIBIDO usar k-fold embaralhado
(`KFold(shuffle=True)`, `train_test_split` com shuffle etc.): em série temporal
ele faz o modelo treinar com o futuro para prever o passado (vazamento, aula 10,
slide 25).
"""

from collections.abc import Iterator

import numpy as np
import pandas as pd

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
    raise NotImplementedError


def divisao_treino_validacao(
    treino: pd.DataFrame,
    meses_validacao: int = config.MESES_VALIDACAO,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa os últimos `meses_validacao` meses do treino como validação.

    Decisão 7 (aula 10, slide 26): hiperparâmetros (k do KNN, número de lags)
    são escolhidos nessa validação, nunca olhando o teste.
    """
    raise NotImplementedError


def walk_forward(
    base: pd.DataFrame,
    meses_treino_inicial: int = config.MESES_TREINO,
) -> Iterator[tuple[pd.DataFrame, pd.DataFrame]]:
    """Gera divisões em janela que avança mês a mês (walk-forward).

    Decisão 7: a cada passo, treina com todos os meses até t e testa no
    mês t+1; depois avança um mês. Deve produzir (treino, teste) com o teste
    sempre de um único mês, posterior a todo o treino.
    """
    raise NotImplementedError


def metricas_regressao(y_real: np.ndarray, y_previsto: np.ndarray) -> dict[str, float]:
    """Calcula o erro em valor: MAE e MSE (aulas 09 e 10).

    Responde "quanto vou gastar?". Deve devolver {"MAE": ..., "MSE": ...}.
    """
    raise NotImplementedError


def direcao(preco_atual: np.ndarray, preco_referencia: np.ndarray) -> np.ndarray:
    """Converte preços em direção: 1 = "sobe", 0 = "não sobe".

    Decisão 7: cada previsão vira "sobe / não sobe" comparando com o preço
    atual. Aplicar tanto ao preço real do mês seguinte quanto ao previsto.

    TODO: decidir se igualdade conta como "não sobe" (padrão sugerido) e se
    haverá tolerância mínima para considerar alta.
    """
    raise NotImplementedError


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
    raise NotImplementedError


def avaliar_modelo(modelo, base: pd.DataFrame, colunas_entrada: list[str], coluna_alvo: str) -> pd.DataFrame:
    """Avalia um modelo com divisão temporal / walk-forward e reúne as métricas.

    Deve treinar e prever respeitando a ordem do tempo, e devolver uma tabela
    com MAE, MSE e as métricas de direção, pronta para comparar com o baseline
    e salvar em reports/tables/.
    """
    raise NotImplementedError
