"""Testes da leitura da CONAB, usando as planilhas reais de data/raw/conab/."""

import pandas as pd
import pytest

from src import config
from src.data_loading import (
    carregar_conab,
    carregar_conab_completo,
    diferencas_entre_abas_leite,
    inspecionar_abas_leite,
    listar_arquivos_conab,
    selecionar_series_conab,
)


@pytest.fixture(scope="module")
def tabela():
    return carregar_conab_completo()


def _linha(tabela, produto, aba):
    achado = tabela[(tabela["produto"] == produto) & (tabela["aba"] == aba)]
    assert len(achado) == 1
    return achado.iloc[0]


def test_lista_as_sete_planilhas():
    arquivos = listar_arquivos_conab()
    assert len(arquivos) == 7
    assert all(arquivo.suffix == ".xls" for arquivo in arquivos)


def test_produto_sem_conab_gera_erro():
    with pytest.raises(ValueError):
        carregar_conab("Tomate")


def test_le_uma_linha_por_aba(tabela):
    assert len(tabela) == 1015
    assert not tabela.duplicated(["planilha", "aba"]).any()


def test_valor_conferido_na_planilha_saca_60kg(tabela):
    linha = _linha(tabela, "Feijão", "Taquarituba-SP-2025")
    assert linha["periodo"] == pd.Period("2025-03", freq="M")
    assert linha["custo_area"] == pytest.approx(14491.97)
    assert linha["custo_unidade_original"] == pytest.approx(316.18825)
    assert linha["kg_unidade"] == 60
    assert linha["custo"] == pytest.approx(316.18825 / 60)
    assert linha["valido"]


def test_leite_fica_em_reais_por_litro(tabela):
    linha = _linha(tabela, "Leite", "S. J. R. Preto-SP-2024")
    assert linha["unidade"] == "R$/l"
    assert linha["custo"] == pytest.approx(3.299256, abs=1e-5)


@pytest.mark.parametrize(
    "produto, aba",
    [
        ("Café", "SP-Franca 2023"),
        ("Café", "Colatina-ES-2019"),
        ("Leite", "Itapetininga-SP-2024"),
    ],
)
def test_copias_sao_invalidas(tabela, produto, aba):
    linha = _linha(tabela, produto, aba)
    assert not linha["valido"]
    assert "copia_de_outra_aba" in linha["problema"]


@pytest.mark.parametrize(
    "produto, aba",
    [("Café", "Patrocínio-MG-2023"), ("Leite", "Cunha-SP-2024")],
)
def test_aba_original_continua_valida(tabela, produto, aba):
    assert _linha(tabela, produto, aba)["valido"]


def test_evidencia_da_copia_de_cunha_em_itapetininga():
    resumo = inspecionar_abas_leite(["Itapetininga-SP-2023", "Itapetininga-SP-2024"])
    assert resumo["municipio_no_titulo"].tolist() == ["ITAPETININGA", "CUNHA"]
    assert resumo["producao_l_dia"].tolist() == [555, 157.5]

    diferencas = diferencas_entre_abas_leite("Itapetininga-SP-2024", "Cunha-SP-2024")
    assert len(diferencas) == 1
    assert "inativado" in diferencas.iloc[0]["Itapetininga-SP-2024"]


def test_saca_inconsistente_e_invalida(tabela):
    linha = _linha(tabela, "Café", "Nova Brasilândia-RO-2025")
    assert not linha["valido"]
    assert "unidade_inconsistente" in linha["problema"]


def test_series_selecionadas_na_janela(tabela):
    series = selecionar_series_conab(tabela)
    assert series.groupby("produto").size().to_dict() == {
        "Arroz": 4,
        "Café": 3,
        "Feijão": 4,
        "Leite": 3,
    }
    assert set(series.loc[series["produto"] == "Leite", "regiao"]) == {"Cunha-SP"}
    assert series["valido"].all()
    assert series["periodo"].min() >= pd.Period(config.PERIODO_INICIO, freq="M")
    assert series["periodo"].max() <= pd.Period(config.PERIODO_FIM, freq="M")
