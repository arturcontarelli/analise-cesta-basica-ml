"""Limpeza da base ICB: tipos, nomes de produto, filtro de produtos e
tratamento de valores faltantes ou inválidos.

O resultado da limpeza é salvo em data/processed/ pelo notebook 01.
"""

import pandas as pd

from src import config


def converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas para os tipos corretos.

    Deve:
    - converter COL_MES e COL_DATA_COLETA para datetime (atenção: podem vir
      como número serial do Excel, contado a partir de 1899-12-30);
    - normalizar COL_MES para o primeiro dia do mês (ou Period mensal);
    - garantir que COL_PRECO, COL_QUANTIDADE e COL_PPK sejam numéricas;
    - remover espaços extras das colunas de texto (Produto, Estab, Marca).
    """
    raise NotImplementedError


def padronizar_nomes_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica nomes duplicados de produto usando `config.MAPA_NOMES_PRODUTOS`.

    Decisão 2 (limpeza obrigatória de nomes): ex. "Pão" -> "Pão Francês",
    "Farinha" -> "Farinha de Trigo". Deve ser aplicada antes de qualquer
    contagem ou análise.

    Deve devolver uma cópia do DataFrame; nomes que não estão no mapa ficam
    inalterados.
    """
    raise NotImplementedError


def filtrar_produtos(df: pd.DataFrame, produtos: list[str] | None = None) -> pd.DataFrame:
    """Mantém apenas os produtos analisados.

    Decisão 2: por padrão usa `config.PRODUTOS`.
    """
    raise NotImplementedError


def remover_registros_invalidos(df: pd.DataFrame) -> pd.DataFrame:
    """Remove registros que não podem ser usados.

    Deve tratar, no mínimo:
    - PPK faltante, zero ou negativo;
    - linhas sem produto, mercado ou mês.

    TODO: decidir na etapa 01 se valores extremos (prováveis erros de
    digitação) serão removidos e com qual critério. Registrar a decisão em
    docs/decisoes.md. Lembrar que a mediana (decisão 3) já reduz o efeito deles.
    """
    raise NotImplementedError


def limpar_base(df: pd.DataFrame, produtos: list[str] | None = None) -> pd.DataFrame:
    """Executa a limpeza completa, na ordem:

    1. `converter_tipos`
    2. `padronizar_nomes_produtos`
    3. `filtrar_produtos`
    4. `remover_registros_invalidos`

    É a função que os notebooks devem chamar, para garantir que todo o grupo
    use exatamente a mesma limpeza (decisão 8).
    """
    raise NotImplementedError
