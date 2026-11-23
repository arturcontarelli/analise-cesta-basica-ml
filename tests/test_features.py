"""Testes de src/features.py (parte C).

Usa séries fictícias pequenas, no formato combinado com a parte A (decisão 9),
para não depender da base real.
"""

import numpy as np
import pandas as pd
import pytest

from src.features import adicionar_variaveis_conab, criar_alvo, criar_lags, montar_base_q1


def _serie_exemplo() -> pd.Series:
    indice = pd.period_range("2024-01", periods=5, freq="M")
    return pd.Series([10, 11, 12, 13, 14], index=indice, dtype=float)


def test_criar_lags_lag1_e_o_preco_atual():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=2)

    assert lags["lag_1"].tolist() == serie.tolist()


def test_criar_lags_lag2_e_o_mes_anterior():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=2)

    assert np.isnan(lags["lag_2"].iloc[0])
    assert lags["lag_2"].iloc[1:].tolist() == serie.iloc[:-1].tolist()


def test_criar_lags_gera_n_colunas_do_tamanho_da_serie():
    serie = _serie_exemplo()
    lags = criar_lags(serie, n_lags=3)

    assert list(lags.columns) == ["lag_1", "lag_2", "lag_3"]
    assert len(lags) == len(serie)


def test_criar_alvo_e_o_preco_do_mes_seguinte():
    serie = _serie_exemplo()
    alvo = criar_alvo(serie)

    assert alvo.name == "alvo"
    assert alvo.iloc[:-1].tolist() == serie.iloc[1:].tolist()
    assert np.isnan(alvo.iloc[-1])


def test_adicionar_variaveis_conab_repete_ultimo_relato_e_conta_idade():
    mes = pd.period_range("2024-01", periods=6, freq="M")
    base = pd.DataFrame({"lag_1": range(6)}, index=mes)
    conab = pd.DataFrame({
        "periodo": pd.PeriodIndex(["2024-01", "2024-04"], freq="M"),
        "custo": [10.0, 12.0],
    })

    resultado = adicionar_variaveis_conab(base, conab)

    assert resultado["custo_conab"].tolist() == [10.0, 10.0, 10.0, 12.0, 12.0, 12.0]
    assert resultado["meses_desde_relato_conab"].tolist() == [0, 1, 2, 0, 1, 2]


def test_adicionar_variaveis_conab_meses_antes_do_primeiro_relato_ficam_nan():
    mes = pd.period_range("2024-01", periods=3, freq="M")
    base = pd.DataFrame({"lag_1": range(3)}, index=mes)
    conab = pd.DataFrame({
        "periodo": pd.PeriodIndex(["2024-03"], freq="M"),
        "custo": [10.0],
    })

    resultado = adicionar_variaveis_conab(base, conab)

    assert resultado["custo_conab"].iloc[:2].isna().all()
    assert resultado["custo_conab"].iloc[2] == 10.0


def test_adicionar_variaveis_conab_defasagem_desloca_para_o_passado():
    mes = pd.period_range("2024-01", periods=4, freq="M")
    base = pd.DataFrame({"lag_1": range(4)}, index=mes)
    conab = pd.DataFrame({
        "periodo": pd.PeriodIndex(["2024-01"], freq="M"),
        "custo": [10.0],
    })

    resultado = adicionar_variaveis_conab(base, conab, defasagem=2)

    assert resultado["custo_conab"].iloc[:2].isna().all()
    assert resultado["custo_conab"].iloc[2:].tolist() == [10.0, 10.0]


def test_montar_base_q1_filtra_produto_e_remove_nan_das_pontas():
    mes = list(pd.period_range("2024-01", periods=6, freq="M"))
    geral = pd.DataFrame({
        "produto": ["Cafe"] * 6 + ["Arroz"] * 6,
        "mes": mes + mes,
        "preco": [10, 11, 12, 13, 14, 15] + [100, 101, 102, 103, 104, 105],
        "n_mercados": [27] * 12,
    })

    base = montar_base_q1(geral, "Cafe", n_lags=2)

    assert list(base.columns) == ["mes", "lag_1", "lag_2", "alvo"]
    assert len(base) == 4  # 6 meses - 1 (sem lag_2) - 1 (sem alvo)
    assert base["lag_1"].max() < 15  # nunca inclui o preço do Arroz
    assert base["mes"].is_monotonic_increasing


def test_montar_base_q1_filtra_conab_pelo_produto():
    mes = list(pd.period_range("2024-01", periods=4, freq="M"))
    geral = pd.DataFrame({
        "produto": ["Arroz"] * 4,
        "mes": mes,
        "preco": [10, 11, 12, 13],
        "n_mercados": [27] * 4,
    })
    conab = pd.DataFrame({
        "produto": ["Arroz", "Arroz", "Feijão"],
        "periodo": pd.PeriodIndex(["2024-01", "2024-03", "2024-01"], freq="M"),
        "custo": [5.0, 6.0, 999.0],
    })

    base = montar_base_q1(geral, "Arroz", n_lags=1, conab=conab)

    assert "custo_conab" in base.columns
    assert (base["custo_conab"] < 999).all()  # nunca usa o custo do Feijão
