# Divisão do trabalho

| Parte | Responsável | O que faz | Arquivos |
|---|---|---|---|
| **A. Limpeza e exploração** | _(nome)_ | Limpa a base (nomes, faltantes, erros de digitação), monta o preço geral (mediana) e define quantos meses um mercado precisa ter para entrar na Q3. | `cleaning.py`, `aggregation.py` (série geral e meses por mercado), notebooks 01 e 02 |
| **B. CONAB** | _(nome)_ | Baixa e lê as planilhas do produtor. Decide qual planilha e região usar e como transformar em dado mensal, ou justifica o descarte. | `data_loading.py` (CONAB), `features.py` (variáveis CONAB), notebook 03 |
| **C. Q1: previsão** | _(nome)_ | Monta lags e divisão temporal. Treina baseline, regressão linear, KNN e ensemble. Escolhe hiperparâmetros sem olhar o teste e interpreta se algum modelo bate o baseline. | `features.py` (lags e alvo), `evaluation.py`, `q1_models.py`, notebook 04 |
| **D. Q3: agrupamento** | _(nome)_ | Calcula o preço relativo de cada mercado. Escolhe o k do K-Means (cotovelo, silhueta, Xie-Beni), interpreta os grupos, calcula a economia em R$ e verifica a estabilidade no tempo. | `aggregation.py` (por mercado), `q3_clustering.py`, notebook 05 |

## Ordem

1. **A** começa primeiro: as outras partes usam a base limpa.
2. **B** pode começar já, porque não depende de ninguém.
3. **C** e **D** podem adiantar o que não depende da base: métricas, divisão temporal e Xie-Beni.

## Todos

- Escrever a seção da própria parte no relatório do grupo.
- Fazer o relatório de extensão individual (modelo no Canvas).
