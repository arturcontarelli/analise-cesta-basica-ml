"""Criação das variáveis de entrada da Q1 (previsão do preço do mês seguinte).

Regra geral: toda variável de uma linha (mês t) só pode usar informação
disponível até o mês t. Nada do futuro pode entrar nas entradas
(decisão 7: evitar vazamento).
"""

import pandas as pd

from src import config


def criar_lags(serie: pd.Series, n_lags: int) -> pd.DataFrame:
    """Cria colunas com os preços dos meses anteriores (lags).

    Para cada mês t, gera `lag_1` = preço em t, `lag_2` = preço em t-1, ...,
    até `lag_{n_lags}`. Decisão 6: a regressão linear e o KNN usam esses lags
    como entrada. O número de lags é hiperparâmetro (escolhido na validação,
    ver `config.LAGS_CANDIDATOS`).

    Linhas iniciais sem histórico suficiente ficam com NaN e devem ser
    descartadas em `montar_base_q1`.
    """
    raise NotImplementedError


def criar_alvo(serie: pd.Series) -> pd.Series:
    """Cria o alvo da Q1: o preço do mês seguinte (t+1).

    Decisão 1 (Q1): prever o preço do mês seguinte de cada produto.
    """
    raise NotImplementedError


def adicionar_variaveis_conab(base: pd.DataFrame, conab: pd.DataFrame, defasagem: int = 0) -> pd.DataFrame:
    """Acrescenta o custo do produtor (CONAB) como variável extra.

    Decisão 5: só para `config.PRODUTOS_CONAB` (Arroz, Feijão, Café, Leite).
    Hipótese: aumento no custo do produtor chega ao mercado alguns meses
    depois, por isso a `defasagem` (em meses).

    TODO: os custos provavelmente são por safra, não por mês. Definir no
    notebook 03 se os valores serão repetidos ou interpolados, e justificar.
    Se não for possível alinhar com os dados mensais, a CONAB é descartada
    (decisão 5).
    """
    raise NotImplementedError


def montar_base_q1(
    geral: pd.DataFrame,
    produto: str,
    n_lags: int,
    conab: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Monta a tabela de modelagem da Q1 para um produto.

    Deve:
    - pegar a série geral do `produto` (saída de `aggregation.serie_geral`);
    - criar os lags (`criar_lags`) e o alvo (`criar_alvo`);
    - se `conab` for informado e o produto estiver em `config.PRODUTOS_CONAB`,
      adicionar as variáveis da CONAB;
    - remover linhas com NaN nas entradas ou no alvo;
    - manter a coluna de mês, em ordem cronológica, para a divisão temporal.
    """
    raise NotImplementedError
