# Pendências da parte C (Q1: previsão)

Levantadas em 24/11/2026, depois de integrar as partes A, B e C na `main`. Nenhum item abaixo quebra o código: os 64 testes passam e os notebooks 03 e 04 rodam sem erro. São pontos de **método e de apresentação**, que pesam na arguição ("rigor nos processos", enunciado).

As decisões são da parte C. As opções listadas são sugestões, não escolhas já feitas. Ao decidir, registre em `docs/decisoes.md` e marque o item aqui como resolvido.

---

## 1. O período de teste muda de produto para produto

**O que acontece:** `evaluation.walk_forward(base, config.MESES_TREINO)` separa treino e teste pela **posição da linha**, não pelo mês. Como `features.montar_base_q1` descarta as primeiras `n_lags − 1` linhas (sem histórico) e a última (sem alvo), sobram `48 − n_lags` linhas, e o teste fica com `12 − n_lags` meses.

| n_lags | Produtos | Meses de teste | Período (mês de entrada) |
|---|---|---|---|
| 1 | Café, Feijão, Tomate, Batata, Pão Francês | 11 | set/2025 a jul/2026 |
| 2 | Banana Nanica, Carne Bovina Coxão Mole | 10 | out/2025 a jul/2026 |
| 3 | Manteiga, Óleo | 9 | nov/2025 a jul/2026 |
| 6 | Arroz, Leite, Farinha de Trigo, Açúcar, Banana Prata | 6 | fev/2026 a jul/2026 |

**Por que importa:**
- O notebook 04 e a decisão 7 dizem que o teste é "meses 37 a 48", o que só vale para `n_lags = 1`.
- Produtos são avaliados em janelas diferentes, então "bateu o baseline em 3 de 14" mistura períodos diferentes.
- Com 6 meses de teste, a matriz de confusão de direção tem 6 pontos (ex.: Arroz `[[2, 0], [4, 0]]`), e precisão e revocação ficam muito instáveis.

**Não há vazamento:** o teste sempre começa depois dos 36 meses que `escolher_hiperparametros` usa.

**Opções:**
- (a) Cortar pela data, como a parte B já faz em `conab_analise.divisao_por_data`. Assim todo produto é testado nos mesmos meses (os 11 de set/2025 a jul/2026).
- (b) Manter o corte por linha e corrigir o texto do notebook 04 e da decisão 7, informando o tamanho do teste por produto.

**Onde:** `src/evaluation.py` (`walk_forward`, `avaliar_modelo`), `notebooks/04_q1_previsao.ipynb`, decisão 7.

---

## 2. O número de lags é escolhido só pelo KNN

**O que acontece:** `q1_models.escolher_hiperparametros` busca `n_lags` e `k` juntos, minimizando o erro de validação **do KNN**. Esse `n_lags` é usado depois também pela regressão linear, pela Random Forest e pelo ensemble.

**Por que importa:** o melhor número de lags para o KNN não é necessariamente o melhor para os outros modelos. Na arguição, a pergunta "como vocês escolheram os lags da regressão linear?" não tem resposta direta hoje.

**Opções:**
- (a) Escolher `n_lags` separadamente para cada modelo, na mesma validação.
- (b) Manter como está e justificar no relatório (um único conjunto de entradas por produto, para comparar os modelos com as mesmas informações).

**Observação relacionada:** o `k` escolhido foi 1 em 7 dos 14 produtos. KNN com `k = 1` copia o vizinho mais próximo e costuma ser instável. Vale comentar no relatório.

---

## 3. O notebook 04 não salva resultados nem tem conclusão

**O que acontece:** o notebook mostra a tabela de 84 linhas (14 produtos × 6 modelos) e a tabela de extrapolação, mas:
- não salva nada em `reports/tables/` nem em `reports/figures/`;
- não tem um resumo de "quem bate o baseline";
- não tem célula de conclusão respondendo à Q1.

**Resultados conferidos na versão integrada** (MAE menor que o baseline):

| Modelo | Produtos | Total |
|---|---|---|
| Regressão linear | Manteiga, Tomate, Batata | 3 de 14 |
| KNN | Óleo, Batata, Banana Nanica | 3 de 14 |
| Ensemble | Manteiga, Óleo, Batata | 3 de 14 |
| Random Forest | Manteiga, Óleo, Banana Nanica | 3 de 14 |

Os números de ensemble e Random Forest batem com o que está em `docs/decisoes.md` e `docs/previsao_q1.md`.

**Sugestão do que salvar** (os nomes seguem o padrão `NN_` dos notebooks 02 e 03):
- `reports/tables/04_q1_resultados.csv`: tabela completa de métricas;
- `reports/tables/04_q1_extrapolacao.csv`: diagnóstico de extrapolação;
- uma figura comparando o MAE de cada modelo com o do baseline, por produto;
- uma célula final com a conclusão (a conclusão negativa já está escrita em `docs/previsao_q1.md`).

---

## 4. Textos desatualizados

Pequenas correções, todas da parte C:

| Onde | O que diz | Situação |
|---|---|---|
| `src/config.py`, linha 158 | `MESES_TREINO`: "TODO: confirmar na etapa 04" | O valor 36 já é usado; tirar o TODO ou ajustar conforme o item 1 |
| `src/config.py`, linha 163 | `MESES_VALIDACAO`: "TODO: definir na etapa 04" | O valor 6 já é usado; tirar o TODO |
| `src/evaluation.py`, linha 104 | `direcao`: "TODO: decidir se igualdade conta como não sobe" | A decisão já está no parágrafo logo abaixo; tirar o TODO |
| `src/q1_models.py`, linha 12, e `docs/decisoes.md`, decisão 6 | Justifica a Random Forest pela relação não linear "entre o custo do produtor e o preço" | A CONAB saiu dos modelos finais (decisão 5). A justificativa que vale hoje é a do gatilho: nenhum modelo das aulas bateu o baseline com folga |
| `src/evaluation.py`, linha 36, e decisão 7 | "testar nos meses 37 a 48" | Ver item 1 |

---

## 5. Revisar a integração

Na integração houve conflito em dois textos da parte C, resolvidos assim:
- `docs/previsao_q1.md`, seção "Onde isso está agora": mantido o texto da `dev` (ensemble, Random Forest, série real). Só a frase da CONAB foi trocada para "já foi testada e ficou fora dos modelos finais (decisão 5, notebook 03)".
- `notebooks/04_q1_previsao.ipynb`, primeira célula: a linha "entradas" agora diz que a CONAB foi testada no notebook 03 e ficou fora dos modelos finais.

Vale a parte C conferir se esses textos ainda dizem o que ela quer.
