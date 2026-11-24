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

# Decisão 5: produtos agrícolas "brutos" com custo do produtor (CONAB). Depois
# da comparação com e sem CONAB (notebook 03), ela fica fora dos modelos finais
# da Q1 e é usada só na comparação e na análise descritiva.
PRODUTOS_CONAB = [
    "Arroz",
    "Feijão",
    "Café",
    "Leite",
]

# Subpasta de data/raw/conab/ de cada produto.
PASTAS_CONAB = {
    "Arroz": "arroz",
    "Feijão": "feijao",
    "Café": "cafe",
    "Leite": "leite",
}

# Planilha e local escolhidos para cada produto (justificativa no notebook 03).
SERIES_CONAB = {
    "Arroz": {"planilha": "Arroz_Irrigado_Serie_Historica_2002-2026.xls", "regiao": "Pelotas-RS"},
    "Feijão": {"planilha": "Feijao_1_Safra_Serie_Historica-1998-2026.xls", "regiao": "Taquarituba-SP"},
    "Café": {"planilha": "seriehistoricacustoscafearabica2003a2025.xls", "regiao": "Franca-SP"},
    "Leite": {"planilha": "Serie_Historica_Leite_SP_2014-2025.xls", "regiao": "Cunha-SP"},
}

# Tabela gerada pelo notebook 03, com todas as abas lidas da CONAB.
ARQUIVO_CONAB_CONSOLIDADO = DIR_DADOS_PROCESSED / "conab_custos.csv"

# Defasagens (em meses) testadas na comparação dos modelos com e sem CONAB.
DEFASAGENS_CONAB = [0, 3]

# Produtos com cobertura completa, usados na comparação anual de custo e preço.
PRODUTOS_CONAB_DESCRITIVA = ["Arroz", "Feijão"]

# ---------------------------------------------------------------------------
# Limpeza (parte A) — decisão 10
# ---------------------------------------------------------------------------
# Base limpa gerada pelo notebook 01 e lida pelas outras etapas.
ARQUIVO_BASE_LIMPA = DIR_DADOS_PROCESSED / "icb_limpo.csv"

# Decisão 10: embalagem padrão (campo Quantidade, em kg/L/unidade) de cada
# produto. Só ela é mantida, para comparar sempre o mesmo item. Valores = a
# quantidade mais comum de cada produto na base (cobre ~99% dos registros);
# na manteiga, exclui potes de 250/500 g, muitos deles margarina.
EMBALAGEM_PADRAO = {
    "Café": 0.5,
    "Arroz": 5.0,
    "Feijão": 1.0,
    "Leite": 1.0,
    "Manteiga": 0.2,
    "Farinha de Trigo": 1.0,
    "Óleo": 0.9,
    "Açúcar": 1.0,
    "Tomate": 1.0,
    "Batata": 1.0,
    "Banana Prata": 1.0,
    "Banana Nanica": 1.0,
    "Carne Bovina Coxão Mole": 1.0,
    "Pão Francês": 1.0,
}

# Decisão 10: um registro é preço atípico (provável erro de digitação) se o
# PPK for mais de FATOR vezes maior ou menor que a mediana do mesmo produto no
# mesmo mês. Ex.: banana a R$ 999/kg, pão a R$ 0,10/kg. Também remove alguns
# preços de hortifrúti perto de 1/3 da mediana (ver limitações da decisão 10).
FATOR_PRECO_ATIPICO = 3

# ---------------------------------------------------------------------------
# Q1 — previsão do preço do mês seguinte
# ---------------------------------------------------------------------------
# Decisão 3: preço geral = mediana do PPK entre mercados, por produto e mês.
ESTATISTICA_PRECO_GERAL = "median"

# Decisão 7: divisão temporal por data (`evaluation.divisao_por_data`).
# Quantidade de meses iniciais usados para escolher hiperparâmetros e treinar;
# o teste final usa os meses seguintes (ver notebook 04, `primeiro_mes_teste`).
MESES_TREINO = 36

# Decisão 7: hiperparâmetros (k do KNN, número de lags) escolhidos numa parte
# separada do treino. Quantidade de meses finais do treino usados como
# validação (`evaluation.divisao_treino_validacao`, corte por data).
MESES_VALIDACAO = 6

# Decisão 6/7: valores candidatos a testar na validação (provisórios).
LAGS_CANDIDATOS = [1, 2, 3, 6]
K_VIZINHOS_CANDIDATOS = [1, 3, 5, 7, 9]

# ---------------------------------------------------------------------------
# Q3 — agrupamento de mercados
# ---------------------------------------------------------------------------
# Decisão 4: só mercados com séries quase completas (40 dos 48 meses ou mais).
# Justificado no notebook 02: nenhum mercado tem de 35 a 40 meses, então
# qualquer corte entre 35 e 41 seleciona os mesmos 25 mercados.
MIN_MESES_MERCADO = 40

# Decisão 4/7: faixa de k testada no K-Means (cotovelo, silhueta, Xie-Beni).
K_CLUSTERS_MIN = 2
K_CLUSTERS_MAX = 8

# Decisão 11: k escolhido no notebook 05. Cotovelo e Xie-Beni apontam k = 3, a
# silhueta fica praticamente empatada entre k = 2, 3 e 4 (0,370 a 0,377) e
# k = 3 tem o melhor pior caso de estabilidade entre os períodos de 12 meses.
K_ESCOLHIDO_Q3 = 3

# Decisão 11: Pão Francês fica fora da Q3. 4 dos 25 mercados quase não têm o
# produto (SUP_36 e SUP_46 nunca, SUP_01 e SUP_47 em 1 mês), e são justamente
# os mais baratos; preencher o valor os puxaria para a média. A Q1 continua
# com os 14 produtos. Justificativa completa em docs/agrupamento_q3.md.
PRODUTOS_FORA_Q3 = ["Pão Francês"]
PRODUTOS_Q3 = [p for p in PRODUTOS if p not in PRODUTOS_FORA_Q3]

# Decisão 11: cesta usada para converter o preço relativo em R$. Quantidades
# mensais da Cesta Básica do DIEESE, Região 1 (inclui SP), Decreto-Lei
# 399/1938 (DIEESE, "Metodologia da Pesquisa Nacional da Cesta Básica de
# Alimentos", ago/2025). Valores na unidade do PPK (kg ou litro).
# - Banana: o DIEESE usa 90 unidades (7,5 dúzias) e converte o preço do kg em
#   preço da dúzia multiplicando por 1,2 (prata) e 1,8 (nanica). Premissa
#   nossa: metade das dúzias de cada variedade.
# - Óleo: o DIEESE usa 750 g; o PPK do óleo é R$/litro, então convertemos pela
#   densidade do óleo de soja (~0,92 kg/L).
DUZIAS_BANANA = 90 / 12
KG_POR_DUZIA_BANANA = {"Banana Prata": 1.2, "Banana Nanica": 1.8}
DENSIDADE_OLEO_KG_POR_L = 0.92
CESTA_DIEESE = {
    "Carne Bovina Coxão Mole": 6.0,
    "Leite": 7.5,
    "Feijão": 4.5,
    "Arroz": 3.0,
    "Farinha de Trigo": 1.5,
    "Batata": 6.0,
    "Tomate": 9.0,
    "Pão Francês": 6.0,
    "Café": 0.6,
    "Açúcar": 3.0,
    "Óleo": 0.75 / DENSIDADE_OLEO_KG_POR_L,
    "Manteiga": 0.75,
    "Banana Prata": DUZIAS_BANANA / 2 * KG_POR_DUZIA_BANANA["Banana Prata"],
    "Banana Nanica": DUZIAS_BANANA / 2 * KG_POR_DUZIA_BANANA["Banana Nanica"],
}

# Decisão 11: o preço de referência da cesta em R$ é a média do preço geral
# nos últimos MESES_PRECO_CESTA meses da base (preço "de hoje").
MESES_PRECO_CESTA = 12

# Decisão 11: períodos de 12 meses (set a ago) usados para medir a
# estabilidade dos grupos no tempo. Todos os 25 mercados aparecem nos 4.
PERIODOS_ESTABILIDADE = [
    ("2022-09", "2023-08"),
    ("2023-09", "2024-08"),
    ("2024-09", "2025-08"),
    ("2025-09", "2026-08"),
]

# ---------------------------------------------------------------------------
# Reprodutibilidade
# ---------------------------------------------------------------------------
# Semente fixa para modelos com aleatoriedade (K-Means, Random Forest etc.),
# para que todos do grupo obtenham os mesmos resultados.
SEMENTE = 42
