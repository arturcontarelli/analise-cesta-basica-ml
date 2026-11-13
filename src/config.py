"""Configuração central do projeto.

Este módulo é a ÚNICA fonte de caminhos, lista de produtos, mapa de nomes
duplicados, produtos com dados da CONAB e parâmetros fixos. Os demais módulos
importam daqui. Se uma decisão mudar, altere aqui e registre o motivo em
docs/decisoes.md.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# Decisão 8: dados originais em data/raw/ (nunca editados); dados gerados em
# data/processed/; figuras e tabelas do relatório em reports/.
# ---------------------------------------------------------------------------
RAIZ_PROJETO = Path(__file__).resolve().parents[1]

DIR_DADOS_RAW = RAIZ_PROJETO / "data" / "raw"
DIR_CONAB = DIR_DADOS_RAW / "conab"  # Decisão 5: planilhas da CONAB
DIR_DADOS_PROCESSED = RAIZ_PROJETO / "data" / "processed"
DIR_FIGURAS = RAIZ_PROJETO / "reports" / "figures"
DIR_TABELAS = RAIZ_PROJETO / "reports" / "tables"

ARQUIVO_ICB = DIR_DADOS_RAW / "ICB_DADOS_2026.xlsx"

# ---------------------------------------------------------------------------
# Colunas da base original (ICB_DADOS_2026.xlsx)
# ---------------------------------------------------------------------------
COL_MES = "Mes_Ano_Data"
COL_DATA_COLETA = "Data_Coleta"
COL_MERCADO = "Estab"
COL_PRODUTO = "Produto"
COL_MARCA = "Marca"
COL_PRECO = "Preco"
COL_QUANTIDADE = "Quantidade"
COL_PPK = "PPK"

# Decisão 3: o preço usado nas análises é o PPK (preço por kg/unidade), que
# torna comparáveis embalagens de tamanhos diferentes.
COL_PRECO_ANALISE = COL_PPK

# Período coberto pela base: set/2022 a ago/2026 (48 meses).
PERIODO_INICIO = "2022-09"
PERIODO_FIM = "2026-08"
TOTAL_MESES = 48

# ---------------------------------------------------------------------------
# Produtos
# Decisão 2: os 14 produtos com cerca de 1.000 registros ou mais, usados nas
# duas questões.
# ---------------------------------------------------------------------------
PRODUTOS = [
    "Café",
    "Arroz",
    "Feijão",
    "Leite",
    "Manteiga",
    "Farinha de Trigo",
    "Óleo",
    "Açúcar",
    "Tomate",
    "Batata",
    "Banana Prata",
    "Banana Nanica",
    "Carne Bovina Coxão Mole",
    "Pão Francês",
]

# Decisão 2 (limpeza obrigatória de nomes): nomes duplicados -> nome padrão.
# Levantado a partir dos valores distintos da coluna Produto. Inclui produtos
# fora do escopo (pernil, acém, macarrão) para que as contagens da exploração fiquem
# corretas mesmo antes do filtro.
MAPA_NOMES_PRODUTOS = {
    "Pão": "Pão Francês",
    "Farinha": "Farinha de Trigo",
    "Macarrão": "Macarrão com Ovos",
    "Carne Coxão Mole": "Carne Bovina Coxão Mole",
    "Carne Acem": "Carne Bovina Acem",
    "Pernil": "Carne Suína Pernil",
    "Carne Pernil": "Carne Suína Pernil",
}

# Decisão 5: custo do produtor (CONAB) como variável extra da Q1, apenas para
# estes 4 produtos agrícolas "brutos".
PRODUTOS_CONAB = [
    "Arroz",
    "Feijão",
    "Café",
    "Leite",
]

# ---------------------------------------------------------------------------
# Q1 — previsão do preço do mês seguinte
# ---------------------------------------------------------------------------
# Decisão 3: preço geral = mediana do PPK entre mercados, por produto e mês.
ESTATISTICA_PRECO_GERAL = "median"

# Decisão 7: divisão temporal. Exemplo do documento: treinar até o mês 36 e
# testar nos meses 37 a 48. TODO: confirmar na etapa 04.
MESES_TREINO = 36

# Decisão 7: hiperparâmetros (k do KNN, número de lags) escolhidos numa parte
# separada do treino. Quantidade de meses finais do treino usados como
# validação. TODO: definir na etapa 04.
MESES_VALIDACAO = 6

# Decisão 6/7: valores candidatos a testar na validação (provisórios).
LAGS_CANDIDATOS = [1, 2, 3, 6]
K_VIZINHOS_CANDIDATOS = [1, 3, 5, 7, 9]

# ---------------------------------------------------------------------------
# Q3 — agrupamento de mercados
# ---------------------------------------------------------------------------
# Decisão 4: só mercados com séries quase completas (~40 dos 48 meses ou mais).
# Valor PROVISÓRIO: deve ser justificado no notebook 02 (gráfico de meses
# disponíveis por mercado).
MIN_MESES_MERCADO = 40

# Decisão 4/7: faixa de k testada no K-Means (cotovelo, silhueta, Xie-Beni).
K_CLUSTERS_MIN = 2
K_CLUSTERS_MAX = 8

# ---------------------------------------------------------------------------
# Reprodutibilidade
# ---------------------------------------------------------------------------
# Semente fixa para modelos com aleatoriedade (K-Means, Random Forest etc.),
# para que todos do grupo obtenham os mesmos resultados.
SEMENTE = 42
