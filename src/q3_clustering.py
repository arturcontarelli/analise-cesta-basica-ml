"""Q3: agrupamento de mercados por perfil de preço.

Decisão 4: dados POR MERCADO, só mercados com série quase completa
(`config.MIN_MESES_MERCADO`). Cada mercado é representado pelo seu preço
relativo em cada produto. Algoritmo: K-Means (aula 11), com k escolhido por
cotovelo, silhueta e índice Xie-Beni (aulas 11 e 12).
"""

import numpy as np
import pandas as pd

from src import config


def montar_matriz_mercados(relativo: pd.DataFrame) -> pd.DataFrame:
    """Monta a matriz de entrada do K-Means: uma linha por mercado, uma coluna
    por produto.

    Recebe a saída de `aggregation.preco_relativo` e resume cada mercado pelo
    preço relativo típico (ex.: mediana no período) de cada produto.

    TODO: definir na etapa 05 como tratar produtos faltantes num mercado
    (imputar 1,0 = "na média", remover o produto ou o mercado) e justificar.
    """
    raise NotImplementedError


def curva_cotovelo(X: np.ndarray, ks: range | None = None) -> pd.DataFrame:
    """Calcula a inércia (soma das distâncias ao centro) do K-Means para cada k.

    Por padrão `ks` vai de `config.K_CLUSTERS_MIN` a `config.K_CLUSTERS_MAX`.
    Usar `random_state=config.SEMENTE`. Usado no gráfico do cotovelo.
    """
    raise NotImplementedError


def silhueta_por_k(X: np.ndarray, ks: range | None = None) -> pd.DataFrame:
    """Calcula o coeficiente de silhueta médio para cada k (aula 12)."""
    raise NotImplementedError


def indice_xie_beni(X: np.ndarray, rotulos: np.ndarray, centros: np.ndarray) -> float:
    """Calcula o índice Xie-Beni de um agrupamento (aula 12). Menor é melhor.

    Versão para agrupamento rígido (K-Means):
        XB = soma(||x_i - c_{rótulo(i)}||^2) / (n * min_{j != l} ||c_j - c_l||^2)

    O numerador mede a compactação dos grupos e o denominador a separação
    entre os centros mais próximos.
    """
    raise NotImplementedError


def xie_beni_por_k(X: np.ndarray, ks: range | None = None) -> pd.DataFrame:
    """Calcula o índice Xie-Beni do K-Means para cada k."""
    raise NotImplementedError


def ajustar_kmeans(X: np.ndarray, k: int):
    """Ajusta o K-Means final com o k escolhido (`random_state=config.SEMENTE`)."""
    raise NotImplementedError


def economia_entre_grupos(matriz: pd.DataFrame, rotulos: np.ndarray, precos_gerais: pd.Series) -> pd.DataFrame:
    """Estima quanto o consumidor economiza (em R$) comprando no grupo mais barato.

    Decisão 1 (Q3): "quanto o consumidor economiza escolhendo bem onde
    comprar?". Deve converter o preço relativo de cada grupo em R$ usando o
    preço geral dos produtos (ex.: custo de uma cesta com 1 unidade/kg de cada
    produto) e comparar os grupos.
    """
    raise NotImplementedError


def estabilidade_temporal(relativo: pd.DataFrame, k: int, periodos: list[tuple[str, str]]) -> pd.DataFrame:
    """Verifica se os grupos se mantêm estáveis no tempo.

    Decisão 4: agrupar os mercados separadamente em cada período (ex.: cada
    ano) e comparar os rótulos (ex.: adjusted Rand index, ou se o mercado
    "barato" continua barato). Se o mercado barato de 2023 virou caro em
    2025, a recomendação não se sustenta.
    """
    raise NotImplementedError
