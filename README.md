# Análise e previsão de preços da cesta básica

Trabalho final da disciplina **Sistemas Inteligentes e Aprendizado de Máquina** (13134), PUC Campinas. Grupo de 4 pessoas.

> **Leia [`docs/decisoes.md`](docs/decisoes.md) antes de alterar qualquer coisa.** Lá está cada decisão do projeto e o motivo dela. Se uma decisão mudar, registre a mudança lá.

## Objetivo (trabalho de extensão)

Este é um trabalho de **extensão**: usamos dados reais de preços de itens da cesta básica, coletados em 51 supermercados (anonimizados) de set/2022 a ago/2026, para gerar conhecimento útil à comunidade. Quem pode usar os resultados:

- **ONGs, bancos de alimentos, prefeituras e famílias**, que planejam o orçamento com antecedência e precisam saber quanto a cesta deve custar no mês seguinte;
- **consumidores**, que não sabem quais mercados são baratos de forma consistente e gastam tempo e transporte pesquisando preço.

O enunciado do professor está em [`docs/enunciado.md`](docs/enunciado.md).

## Questões

**Q1: é possível prever o preço do mês seguinte de cada produto melhor do que simplesmente repetir o preço atual?** (aprendizado supervisionado)
- Usa o preço **geral**: a mediana do preço por kg/unidade (PPK) entre os mercados, por produto e mês.
- Modelos: baseline ingênuo (repete o preço atual), regressão linear, KNN e ensemble. Um modelo extra (provavelmente Random Forest) será decidido depois dos primeiros resultados.
- Custo do produtor (CONAB) como variável extra para Arroz, Feijão, Café e Leite.
- Avaliação com **divisão temporal** (nunca k-fold embaralhado): erro em valor (MAE, MSE) e acerto de direção sobe/não sobe (matriz de confusão, acurácia, precisão, revocação).

**Q3: existem mercados consistentemente mais baratos? Quanto o consumidor economiza escolhendo bem onde comprar?** (aprendizado não supervisionado)
- Usa os dados **por mercado**, só de mercados com cerca de 40 dos 48 meses ou mais.
- K-Means, com k escolhido por cotovelo, silhueta e índice Xie-Beni, e verificação da estabilidade dos grupos no tempo.

Produtos analisados: Café, Arroz, Feijão, Leite, Manteiga, Farinha de Trigo, Óleo, Açúcar, Tomate, Batata, Banana Prata, Banana Nanica, Carne Bovina Coxão Mole e Pão Francês. Macarrão com Ovos entra se sobreviver à limpeza.

## Estrutura

```
analise-cesta-basica-ml/
├── data/
│   ├── raw/            # dados originais, NUNCA editados
│   │   ├── ICB_DADOS_2026.xlsx
│   │   └── conab/      # planilhas de custo do produtor (ver README da pasta)
│   └── processed/      # dados limpos gerados pelo código
├── notebooks/          # etapas numeradas, na ordem de execução
├── src/                # lógica compartilhada (os notebooks importam daqui)
│   └── config.py       # fonte única de caminhos, produtos e parâmetros
├── reports/
│   ├── figures/        # gráficos do relatório
│   └── tables/         # tabelas do relatório
└── docs/
    ├── enunciado.md
    └── decisoes.md     # LEIA ANTES DE ALTERAR QUALQUER COISA
```

Regras de organização:
- Toda lógica fica em `src/`; os notebooks só chamam funções e mostram resultados. Assim todos usam a mesma limpeza e a mesma avaliação.
- Lista de produtos, nomes duplicados, caminhos e parâmetros ficam **só** em `src/config.py`.
- Os arquivos em `data/raw/` nunca são editados. Tudo que o código gera vai para `data/processed/` ou `reports/`.

## Instalação

Requer Python 3.10 ou superior.

```bash
# na pasta do repositório
python -m venv .venv

# ativar o ambiente
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
jupyter notebook
```

## Ordem de execução

Rode os notebooks na ordem; cada um depende dos arquivos gerados pelos anteriores.

| # | Notebook | O que faz |
|---|---|---|
| 1 | `notebooks/01_limpeza.ipynb` | Lê a base, unifica nomes de produto, filtra produtos e trata faltantes. Salva a base limpa em `data/processed/`. |
| 2 | `notebooks/02_exploracao.ipynb` | Explora as séries, a cobertura por mercado e justifica o mínimo de meses por mercado. |
| 3 | `notebooks/03_conab.ipynb` | Lê as planilhas da CONAB e verifica se dá para alinhar com os dados mensais (ou justifica o descarte). |
| 4 | `notebooks/04_q1_previsao.ipynb` | Q1: modelos de previsão do preço do mês seguinte, avaliados com divisão temporal. |
| 5 | `notebooks/05_q3_agrupamento.ipynb` | Q3: agrupamento de mercados com K-Means e estimativa da economia em R$. |
