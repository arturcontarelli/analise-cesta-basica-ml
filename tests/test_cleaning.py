"""Testes da limpeza (parte A) com tabelas pequenas montadas à mão."""

import pandas as pd

from src import cleaning, config


def _base(linhas):
    colunas = [
        config.COL_MES, config.COL_DATA_COLETA, config.COL_MERCADO, config.COL_PRODUTO,
        config.COL_MARCA, config.COL_PRECO, config.COL_QUANTIDADE, config.COL_PPK,
    ]
    return pd.DataFrame(linhas, columns=colunas)


def _linha(produto="Leite", preco=5.0, qtd=1.0, mercado="SUP_01", marca="X",
           mes="2024-01-01", coleta="2024-01-10"):
    return [pd.Timestamp(mes), pd.Timestamp(coleta), mercado, produto, marca,
            preco, qtd, preco / qtd]


def test_converte_serial_do_excel_e_normaliza_mes():
    df = _base([_linha()])
    df[config.COL_MES] = 45306.0  # 15/01/2024 no Excel
    df[config.COL_DATA_COLETA] = 45306.0
    saida = cleaning.converter_tipos(df)
    assert saida[config.COL_MES].iloc[0] == pd.Timestamp("2024-01-01")
    assert saida[config.COL_DATA_COLETA].iloc[0] == pd.Timestamp("2024-01-15")


def test_converter_tipos_mantem_marca_vazia_e_tira_espacos():
    df = _base([_linha(produto=" Leite ", marca=None)])
    saida = cleaning.converter_tipos(df)
    assert saida[config.COL_PRODUTO].iloc[0] == "Leite"
    assert pd.isna(saida[config.COL_MARCA].iloc[0])


def test_padroniza_nomes_duplicados():
    df = _base([_linha(produto="Pão"), _linha(produto="Farinha"), _linha(produto="Leite")])
    saida = cleaning.padronizar_nomes_produtos(df)
    assert list(saida[config.COL_PRODUTO]) == ["Pão Francês", "Farinha de Trigo", "Leite"]


def test_remove_registros_invalidos():
    df = _base([_linha(), _linha(preco=0.0), _linha(mercado=None)])
    df.loc[2, config.COL_MERCADO] = None
    assert len(cleaning.remover_registros_invalidos(df)) == 1


def test_remove_so_duplicatas_exatas():
    df = _base([_linha(), _linha(), _linha(preco=6.0), _linha(coleta="2024-01-20")])
    # 2 primeiras idênticas; as outras diferem no preço ou no dia e ficam.
    assert len(cleaning.remover_duplicatas(df)) == 3


def test_filtra_embalagem_padrao():
    df = _base([
        _linha(produto="Manteiga", preco=13.99, qtd=0.2),
        _linha(produto="Manteiga", preco=8.0, qtd=0.5),
        _linha(produto="Tomate", preco=8.99, qtd=20.0),
    ])
    saida = cleaning.filtrar_embalagem_padrao(df)
    assert list(saida[config.COL_QUANTIDADE]) == [0.2]


def test_embalagem_padrao_exige_produto_conhecido():
    df = _base([_linha(produto="Produto Novo")])
    try:
        cleaning.filtrar_embalagem_padrao(df)
    except ValueError:
        return
    raise AssertionError("deveria acusar produto sem embalagem padrão")


def test_remove_precos_atipicos_pela_mediana_do_mes():
    precos = [5.0, 5.2, 4.8, 5.1, 999.0, 0.10]
    df = _base([_linha(produto="Banana Nanica", preco=p, mercado=f"SUP_{i}") for i, p in enumerate(precos)])
    saida = cleaning.remover_precos_atipicos(df, fator=3)
    assert sorted(saida[config.COL_PPK]) == [4.8, 5.0, 5.1, 5.2]


def test_atipico_compara_so_com_o_mesmo_mes():
    # R$ 10 é normal em dezembro (mediana 10), mesmo sendo 3x o preço de janeiro.
    df = _base([
        _linha(preco=3.0, mes="2024-01-01"), _linha(preco=3.1, mes="2024-01-01"),
        _linha(preco=10.0, mes="2024-12-01"), _linha(preco=9.9, mes="2024-12-01"),
    ])
    assert len(cleaning.remover_precos_atipicos(df, fator=3)) == 4


def test_limpar_base_devolve_resumo_por_etapa():
    df = _base([_linha(), _linha(), _linha(produto="Ovo"), _linha(produto="Pão", preco=16.0)])
    limpa, resumo = cleaning.limpar_base(df)
    assert len(limpa) == 2
    assert resumo["linhas"].iloc[0] == 4
    assert resumo["linhas"].iloc[-1] == 2
    assert resumo["removidas"].sum() == 2
