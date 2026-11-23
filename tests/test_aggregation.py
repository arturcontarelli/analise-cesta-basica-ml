"""Testes da agregação (parte A) com tabelas pequenas montadas à mão."""

import pandas as pd

from src import aggregation, config


def _base(registros):
    """registros: lista de (mes, mercado, produto, ppk)."""
    return pd.DataFrame(
        [
            {config.COL_MES: pd.Timestamp(m), config.COL_MERCADO: e,
             config.COL_PRODUTO: p, config.COL_PPK: v}
            for m, e, p, v in registros
        ]
    )


def test_mediana_em_duas_etapas_da_um_voto_por_mercado():
    # SUP_01 tem 3 marcas caras; SUP_02 e SUP_03 uma barata cada.
    # Mediana direta de [10, 10, 10, 4, 5] = 10; em 2 etapas: mediana de [10, 4, 5] = 5.
    df = _base([
        ("2024-01-01", "SUP_01", "Arroz", 10), ("2024-01-01", "SUP_01", "Arroz", 10),
        ("2024-01-01", "SUP_01", "Arroz", 10), ("2024-01-01", "SUP_02", "Arroz", 4),
        ("2024-01-01", "SUP_03", "Arroz", 5),
    ])
    geral = aggregation.serie_geral(df)
    assert geral["preco"].iloc[0] == 5
    assert geral["n_mercados"].iloc[0] == 3


def test_serie_geral_segue_o_contrato_da_decisao_9():
    df = _base([("2024-01-01", "SUP_01", "Arroz", 5)])
    geral = aggregation.serie_geral(df)
    assert list(geral.columns) == ["produto", "mes", "preco", "n_mercados"]
    assert isinstance(geral["mes"].iloc[0], pd.Period)


def test_mes_sem_coleta_aparece_como_nan():
    df = _base([
        ("2024-01-01", "SUP_01", "Arroz", 5),
        ("2024-03-01", "SUP_01", "Arroz", 6),
    ])
    geral = aggregation.serie_geral(df)
    assert list(geral["mes"].astype(str)) == ["2024-01", "2024-02", "2024-03"]
    fevereiro = geral[geral["mes"] == pd.Period("2024-02", "M")].iloc[0]
    assert pd.isna(fevereiro["preco"]) and fevereiro["n_mercados"] == 0


def test_series_por_mercado_filtra_mercados():
    df = _base([
        ("2024-01-01", "SUP_01", "Arroz", 5), ("2024-01-01", "SUP_02", "Arroz", 6),
    ])
    saida = aggregation.series_por_mercado(df, mercados=["SUP_02"])
    assert list(saida["mercado"]) == ["SUP_02"]
    assert list(saida.columns) == ["produto", "mes", "mercado", "preco", "n_registros"]


def test_meses_e_selecao_de_mercados():
    df = _base([
        ("2024-01-01", "SUP_01", "Arroz", 5), ("2024-02-01", "SUP_01", "Arroz", 5),
        ("2024-02-01", "SUP_01", "Leite", 5), ("2024-01-01", "SUP_02", "Arroz", 5),
    ])
    meses = aggregation.meses_por_mercado(df)
    assert meses.to_dict() == {"SUP_01": 2, "SUP_02": 1}
    assert aggregation.selecionar_mercados(df, min_meses=2) == ["SUP_01"]
