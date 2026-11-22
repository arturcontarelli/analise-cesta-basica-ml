"""Criação das variáveis de entrada da Q1 (previsão do preço do mês seguinte).

Regra geral: toda variável de uma linha (mês t) só pode usar informação
disponível até o mês t. Nada do futuro pode entrar nas entradas
(decisão 7: evitar vazamento).
"""

import numpy as np
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
    colunas = {f"lag_{i}": serie.shift(i - 1) for i in range(1, n_lags + 1)}
    return pd.DataFrame(colunas, index=serie.index)


def criar_alvo(serie: pd.Series) -> pd.Series:
    """Cria o alvo da Q1: o preço do mês seguinte (t+1).

    Decisão 1 (Q1): prever o preço do mês seguinte de cada produto.
    """
    return serie.shift(-1).rename("alvo")


def adicionar_variaveis_conab(base: pd.DataFrame, conab: pd.DataFrame, defasagem: int = 0) -> pd.DataFrame:
    """Acrescenta o custo do produtor (CONAB) como variável extra.

    Decisão 5 (combinada com a parte C): a CONAB publica só 1 valor por ano
    por local (notebook 03), então não há como recuperar os meses entre dois
    relatos sem olhar o relato seguinte — isso seria vazamento (decisão 7).
    Por isso o valor é repetido (forward-fill) a partir do último relato já
    publicado até cada mês de `base`; meses antes do primeiro relato ficam
    NaN (não há informação a repetir) e são descartados em `montar_base_q1`.

    `conab` deve vir filtrada para um único produto (colunas `periodo` e
    `custo`, saída de `data_loading.selecionar_series_conab`).

    Colunas adicionadas:
    - `custo_conab`: último custo do produtor conhecido até o mês.
    - `meses_desde_relato_conab`: idade dessa informação (0 no mês do
      relato, 1 no mês seguinte...), para o modelo aprender a dar menos peso
      a um custo "velho" em vez de isso ser decidido na mão.

    `defasagem` desloca as duas colunas para ainda mais no passado (nunca
    para o futuro), pela hipótese de que o custo do produtor leva tempo
    para chegar ao mercado.
    """
    custo_mensal = conab.sort_values("periodo").set_index("periodo")["custo"].reindex(base.index)
    relatado = custo_mensal.notna()

    posicao = np.arange(len(base))
    posicao_ultimo_relato = pd.Series(np.where(relatado, posicao, np.nan), index=base.index).ffill()

    base = base.copy()
    base["custo_conab"] = custo_mensal.ffill().shift(defasagem)
    base["meses_desde_relato_conab"] = pd.Series(posicao - posicao_ultimo_relato, index=base.index).shift(defasagem)
    return base


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
      adicionar as variáveis da CONAB (filtrando `conab` para esse produto,
      já que a tabela de `selecionar_series_conab` traz os 4 produtos juntos);
    - remover linhas com NaN nas entradas ou no alvo;
    - manter a coluna de mês, em ordem cronológica, para a divisão temporal.
    """
    serie = (
        geral[geral["produto"] == produto].sort_values("mes").set_index("mes")["preco"]
    )
    base = criar_lags(serie, n_lags)
    base["alvo"] = criar_alvo(serie)

    if conab is not None and produto in config.PRODUTOS_CONAB:
        base = adicionar_variaveis_conab(base, conab[conab["produto"] == produto])

    base = base.reset_index().dropna()
    return base.sort_values("mes").reset_index(drop=True)
