"""Testes da Q3 (parte D) com dados pequenos montados à mão."""

import numpy as np
import pandas as pd
import pytest

from src import config, q3_clustering


def _relativo(registros):
    """registros: lista de (mes, mercado, produto, relativo)."""
    return pd.DataFrame(
        [{"mes": pd.Period(m, "M"), "mercado": e, "produto": p, "relativo": r} for m, e, p, r in registros]
    )


def _dois_blocos():
    """6 mercados em 2 produtos: 3 baratos (~0,8) e 3 caros (~1,2)."""
    return np.array([[0.80, 0.81], [0.79, 0.80], [0.81, 0.79], [1.20, 1.21], [1.19, 1.20], [1.21, 1.19]])


# ---------------------------------------------------------------------------
# Matriz de entrada
# ---------------------------------------------------------------------------
def test_matriz_usa_mediana_e_so_os_produtos_pedidos():
    rel = _relativo([
        ("2024-01", "SUP_01", "Arroz", 0.8), ("2024-02", "SUP_01", "Arroz", 0.9),
        ("2024-03", "SUP_01", "Arroz", 2.0),  # mês atípico: a mediana ignora
        ("2024-01", "SUP_01", "Pão Francês", 1.0),
    ])
    matriz = q3_clustering.montar_matriz_mercados(rel, produtos=["Arroz"])
    assert matriz.loc["SUP_01", "Arroz"] == pytest.approx(0.9)
    assert list(matriz.columns) == ["Arroz"]


def test_pao_frances_fora_da_q3():
    assert "Pão Francês" not in config.PRODUTOS_Q3
    assert len(config.PRODUTOS_Q3) == len(config.PRODUTOS) - 1


def test_matriz_nao_imputa_produto_faltante():
    rel = _relativo([
        ("2024-01", "SUP_01", "Arroz", 0.8), ("2024-01", "SUP_01", "Leite", 1.0),
        ("2024-01", "SUP_02", "Arroz", 1.1),
    ])
    with pytest.raises(ValueError, match="SUP_02"):
        q3_clustering.montar_matriz_mercados(rel, produtos=["Arroz", "Leite"])


def test_matriz_filtra_periodo():
    rel = _relativo([
        ("2024-01", "SUP_01", "Arroz", 0.8), ("2024-06", "SUP_01", "Arroz", 1.2),
    ])
    matriz = q3_clustering.montar_matriz_mercados(rel, produtos=["Arroz"], inicio="2024-05", fim="2024-12")
    assert matriz.loc["SUP_01", "Arroz"] == pytest.approx(1.2)


# ---------------------------------------------------------------------------
# K-Means e escolha de k
# ---------------------------------------------------------------------------
def test_ordenar_grupos_deixa_o_mais_barato_como_zero():
    X = _dois_blocos()
    rotulos = np.array([1, 1, 1, 0, 0, 0])  # numeração "invertida", como o K-Means pode devolver
    assert list(q3_clustering.ordenar_grupos(X, rotulos)) == [0, 0, 0, 1, 1, 1]


def test_kmeans_separa_dois_blocos_e_e_reprodutivel():
    X = _dois_blocos()
    a = q3_clustering.ordenar_grupos(X, q3_clustering.ajustar_kmeans(X, 2).labels_)
    b = q3_clustering.ordenar_grupos(X, q3_clustering.ajustar_kmeans(X, 2).labels_)
    assert list(a) == [0, 0, 0, 1, 1, 1]
    assert list(a) == list(b)


def test_xie_beni_confere_com_calculo_manual():
    X = np.array([[0.0], [2.0], [10.0], [12.0]])
    rotulos = np.array([0, 0, 1, 1])
    centros = np.array([[1.0], [11.0]])
    # compactação = 1 + 1 + 1 + 1 = 4; separação = 10^2 = 100; XB = 4 / (4 * 100)
    assert q3_clustering.indice_xie_beni(X, rotulos, centros) == pytest.approx(0.01)


def test_criterios_apontam_k2_em_dois_blocos():
    tabela = q3_clustering.avaliar_k(_dois_blocos(), ks=range(2, 5))
    assert list(tabela.columns) == ["k", "inercia", "silhueta", "xie_beni"]
    assert tabela.loc[tabela["silhueta"].idxmax(), "k"] == 2
    assert tabela.loc[tabela["xie_beni"].idxmin(), "k"] == 2
    assert tabela["inercia"].is_monotonic_decreasing


# ---------------------------------------------------------------------------
# Economia em R$
# ---------------------------------------------------------------------------
def test_cesta_dieese_converte_banana_e_oleo():
    # 90 bananas = 7,5 dúzias; metade de cada: 3,75 dz * 1,2 kg e 3,75 dz * 1,8 kg.
    assert config.CESTA_DIEESE["Banana Prata"] == pytest.approx(4.5)
    assert config.CESTA_DIEESE["Banana Nanica"] == pytest.approx(6.75)
    assert config.CESTA_DIEESE["Óleo"] == pytest.approx(0.75 / 0.92)
    assert set(config.CESTA_DIEESE) == set(config.PRODUTOS)


def test_economia_entre_grupos():
    matriz = pd.DataFrame(
        {"Arroz": [0.8, 0.8, 1.2], "Leite": [0.9, 0.9, 1.1]}, index=["SUP_01", "SUP_02", "SUP_03"]
    )
    precos = pd.Series({"Arroz": 5.0, "Leite": 4.0})
    cesta = {"Arroz": 2.0, "Leite": 10.0}
    tabela = q3_clustering.economia_entre_grupos(matriz, np.array([0, 0, 1]), precos, cesta)
    # mediana: 2*5 + 10*4 = 50; grupo 0: 2*5*0,8 + 10*4*0,9 = 44; grupo 1: 2*5*1,2 + 10*4*1,1 = 56
    assert list(tabela["custo_cesta"]) == pytest.approx([44.0, 56.0])
    assert list(tabela["dif_mediana_rs"]) == pytest.approx([-6.0, 6.0])
    assert tabela.loc[0, "economia_vs_mais_caro_rs_mes"] == pytest.approx(12.0)
    assert tabela.loc[0, "economia_vs_mais_caro_rs_ano"] == pytest.approx(144.0)
    assert tabela.loc[0, "n_mercados"] == 2


def test_preco_referencia_usa_ultimos_meses():
    geral = pd.DataFrame({
        "produto": ["Arroz"] * 3,
        "mes": pd.period_range("2024-01", periods=3, freq="M"),
        "preco": [1.0, 4.0, 6.0],
    })
    assert q3_clustering.preco_referencia_cesta(geral, meses=2)["Arroz"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Estabilidade no tempo
# ---------------------------------------------------------------------------
def test_estabilidade_perfeita_quando_os_grupos_nao_mudam(monkeypatch):
    monkeypatch.setattr(config, "PRODUTOS_Q3", ["Arroz", "Leite"])
    registros = []
    for mes in ["2024-01", "2024-02", "2025-01", "2025-02"]:
        for i, (a, b) in enumerate(_dois_blocos()):
            registros += [(mes, f"SUP_{i}", "Arroz", a), (mes, f"SUP_{i}", "Leite", b)]
    rel = _relativo(registros)
    periodos = [("2024-01", "2024-12"), ("2025-01", "2025-12")]

    grupos = q3_clustering.grupos_por_periodo(rel, 2, periodos)
    assert list(grupos.columns) == ["completo", "2024-01 a 2024-12", "2025-01 a 2025-12"]

    tabela = q3_clustering.estabilidade_temporal(rel, 2, periodos)
    assert list(tabela["ari_vs_completo"]) == pytest.approx([1.0, 1.0])
    assert list(tabela["pct_mesmo_grupo"]) == pytest.approx([100.0, 100.0])
    assert np.isnan(tabela.loc[0, "ari_vs_anterior"])
