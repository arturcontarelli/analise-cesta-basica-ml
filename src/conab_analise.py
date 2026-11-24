"""Análises da CONAB (parte B): comparação na Q1 e variação anual.

Decisão 5: a CONAB fica fora dos modelos finais da Q1. Este módulo guarda a
evidência dessa escolha, reutilizando as funções da Q1 sem alterá-las.
"""

import numpy as np
import pandas as pd

from src import config, evaluation, features, q1_models

COLUNAS_CONAB = ["custo_conab", "meses_desde_relato_conab"]


def _avaliar(modelo, base: pd.DataFrame, colunas: list[str], primeiro_mes_teste: pd.Period) -> dict:
    """Avalia um modelo no walk-forward por data (`evaluation.divisao_por_data`)."""
    reais, previstos, atuais = [], [], []
    for treino, teste in evaluation.divisao_por_data(base, primeiro_mes_teste):
        modelo.fit(treino[colunas], treino["alvo"])
        previstos.append(modelo.predict(teste[colunas])[0])
        reais.append(teste["alvo"].iloc[0])
        atuais.append(teste["lag_1"].iloc[0])

    reais, previstos, atuais = np.array(reais), np.array(previstos), np.array(atuais)
    return {
        "MAE": evaluation.metricas_regressao(reais, previstos)["MAE"],
        "acuracia": evaluation.metricas_direcao(atuais, reais, previstos)["acuracia"],
        "n_teste": len(reais),
    }


def comparar_modelos_com_sem_conab(
    geral: pd.DataFrame,
    conab: pd.DataFrame,
    produtos: list[str] | None = None,
    defasagens: list[int] | None = None,
) -> pd.DataFrame:
    """Compara os modelos da Q1 com e sem as variáveis da CONAB.

    Para a comparação ser justa, os dois lados usam os mesmos meses de teste,
    as mesmas linhas de treino e os hiperparâmetros escolhidos só no treino.

    Args:
        geral: saída de `aggregation.serie_geral`.
        conab: saída de `data_loading.selecionar_series_conab`.
        produtos: por padrão, `config.PRODUTOS_CONAB`.
        defasagens: por padrão, `config.DEFASAGENS_CONAB`.

    Returns:
        Tabela longa com uma linha por produto, defasagem e modelo.
    """
    produtos = config.PRODUTOS_CONAB if produtos is None else produtos
    defasagens = config.DEFASAGENS_CONAB if defasagens is None else defasagens
    primeiro_mes_teste = sorted(geral["mes"].unique())[config.MESES_TREINO]

    linhas = []
    for produto in produtos:
        hiper = q1_models.escolher_hiperparametros(geral[geral["mes"] < primeiro_mes_teste], produto)
        n_lags, k = hiper["n_lags"], hiper["k"]
        lags = [f"lag_{i}" for i in range(1, n_lags + 1)]
        base = features.montar_base_q1(geral, produto, n_lags).set_index("mes")

        for defasagem in defasagens:
            pareada = (
                features.adicionar_variaveis_conab(
                    base, conab[conab["produto"] == produto], defasagem=defasagem
                )
                .dropna()
                .rename_axis("mes")
                .reset_index()
            )
            modelos = {
                "baseline": (q1_models.BaselineIngenuo(), lags),
                "linear": (q1_models.criar_regressao_linear(), lags),
                "linear+CONAB": (q1_models.criar_regressao_linear(), lags + COLUNAS_CONAB),
                "knn": (q1_models.criar_knn(k), lags),
                "knn+CONAB": (q1_models.criar_knn(k), lags + COLUNAS_CONAB),
            }
            for nome, (modelo, colunas) in modelos.items():
                linhas.append({
                    "produto": produto,
                    "defasagem": defasagem,
                    "n_lags": n_lags,
                    "k": k,
                    "n_treino_inicial": int((pareada["mes"] < primeiro_mes_teste).sum()),
                    "modelo": nome,
                    **_avaliar(modelo, pareada, colunas, primeiro_mes_teste),
                })
    return pd.DataFrame(linhas)


def comparar_variacao_anual(
    geral: pd.DataFrame,
    conab: pd.DataFrame,
    produtos: list[str] | None = None,
) -> pd.DataFrame:
    """Compara a variação anual do custo do produtor e do preço de mercado.

    O preço é lido no mesmo mês de referência do custo. A análise é descritiva:
    com poucas comparações, não mede causalidade nem defasagem.
    """
    produtos = config.PRODUTOS_CONAB_DESCRITIVA if produtos is None else produtos
    linhas = []
    for produto in produtos:
        custos = conab[conab["produto"] == produto].sort_values("periodo")
        precos = geral[geral["produto"] == produto].set_index("mes")["preco"]
        for (_, anterior), (_, atual) in zip(custos.iloc[:-1].iterrows(), custos.iloc[1:].iterrows()):
            preco_anterior = precos[anterior["periodo"]]
            preco_atual = precos[atual["periodo"]]
            var_custo = (atual["custo"] / anterior["custo"] - 1) * 100
            var_preco = (preco_atual / preco_anterior - 1) * 100
            linhas.append({
                "produto": produto,
                "periodo_inicial": anterior["periodo"],
                "periodo_final": atual["periodo"],
                "custo_inicial": anterior["custo"],
                "custo_final": atual["custo"],
                "preco_inicial": preco_anterior,
                "preco_final": preco_atual,
                "var_custo_pct": var_custo,
                "var_preco_pct": var_preco,
                "mesma_direcao": bool(np.sign(var_custo) == np.sign(var_preco)),
            })
    return pd.DataFrame(linhas)
