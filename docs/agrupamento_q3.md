# Q3: agrupamento de mercados (parte D)

**Questão:** existem mercados consistentemente mais baratos? Quanto o consumidor economiza escolhendo bem onde comprar?

Este documento registra as escolhas da parte D e o motivo de cada uma. O resumo está na decisão 11 de [`decisoes.md`](decisoes.md). O código está em `src/aggregation.py` (`preco_relativo`) e `src/q3_clustering.py`, e os resultados no notebook `05_q3_agrupamento.ipynb`.

Responsável: Guilherme. Última revisão: 24/11/2026.

---

## 1. Pão Francês fica fora da Q3

**Decisão:** o agrupamento e a conta da economia usam **13 produtos**, sem o Pão Francês (`config.PRODUTOS_FORA_Q3`). A Q1 continua com os 14.

**O problema:** o K-Means precisa do preço relativo de todos os produtos em todos os mercados. No pão isso não acontece entre os 25 mercados da Q3:

| Mercado | Meses com Pão Francês (de 48) | Posição no índice de preço (1 = mais barato) |
|---|---|---|
| SUP_46 | 0 | 1º |
| SUP_06 | 12 | 2º |
| SUP_47 | 1 | 3º |
| SUP_01 | 1 | 4º |
| SUP_36 | 0 | 7º |

Os outros 20 mercados têm pão em 39 a 48 meses.

**Por que tirar o produto, e não preencher nem tirar os mercados:**
- **Os mercados sem pão são justamente os mais baratos.** Os 4 primeiros do índice de preço (nos outros 13 produtos) estão na tabela acima. Provavelmente são atacarejos sem padaria.
- **Preencher com 1,0 ("na média")** colocaria um valor inventado justamente nos mercados mais interessantes e os puxaria para o meio, enfraquecendo a resposta da Q3.
- **Tirar esses mercados** apagaria 2 a 4 dos 25 mercados, que são os mais baratos, ou seja, a própria resposta da pergunta.
- **Quase não se perde informação.** O pão é o produto em que os mercados menos diferem entre si: desvio-padrão de 5,7% no preço relativo típico, contra 21% na banana nanica e na batata e 6,5% no café, o segundo menor.

**Custo da escolha:** o pão é 13% da Cesta Básica do DIEESE a preços de hoje (R$ 109,58 de R$ 845,59). A economia em R$ (seção 5) vale para os outros 87% da cesta.

---

## 2. Preço relativo e matriz de entrada

**Decisão:** cada mercado é descrito, em cada produto, pela mediana de `preço do mercado ÷ preço geral` no período (`aggregation.preco_relativo` e `q3_clustering.montar_matriz_mercados`). Assim, 1,10 significa 10% acima da mediana entre mercados no mesmo mês.

**Por quê:**
- **A razão, e não a diferença em R$,** põe produtos de preços muito diferentes na mesma escala (café a ~R$ 67/kg, açúcar a ~R$ 4,50/kg).
- **Comparar com o mesmo mês** tira a inflação e a safra da conta: um mercado não parece caro só porque foi coletado num mês de alta.
- **O preço geral usa os 51 estabelecimentos,** como na Q1 (decisão 3). A matriz usa os 25 mercados da decisão 4.
- **A mediana dos meses** resume o preço típico do mercado sem ser puxada por um mês de promoção ou de erro.
- **Nada é imputado.** Se faltar um produto num mercado, `montar_matriz_mercados` para com erro. Sem o pão, nenhuma célula fica vazia, nem no período completo nem em cada período de 12 meses.

---

## 3. Sem padronização antes do K-Means

**Decisão:** o preço relativo entra no K-Means como está, sem `StandardScaler`.

**Por quê:**
- **As 13 colunas já estão na mesma unidade** (proporção da mediana). A padronização serve para colunas em unidades diferentes, o que não é o caso aqui.
- **Sem padronizar, a distância entre dois mercados é diferença de preço de verdade.** O hortifrúti pesa mais porque é onde os mercados realmente diferem: o desvio entre mercados vai de 13% a 21% em banana, batata e tomate, contra 6% a 7% em arroz e café.
- **Padronizar daria a uma diferença de 6% no café o mesmo peso de uma de 21% na banana,** o que amplifica diferenças pequenas e mais ruidosas.

---

## 4. Escolha de k

**Decisão:** k = 3 (`config.K_ESCOLHIDO_Q3`), testando k de 2 a 8.

| Critério | Resultado |
|---|---|
| Cotovelo | maior queda da inércia de k = 2 para 3 (−0,99); de 3 para 4 cai só −0,39 |
| Xie-Beni | mínimo em k = 3 (0,244) |
| Silhueta | praticamente empatada em k = 2, 3 e 4 (0,370, 0,375 e 0,377); não desempata |
| Estabilidade no tempo | k = 3 tem o melhor pior caso (ARI mínimo de 0,67 contra o período completo; 0,44 em k = 2 e 0,62 em k = 4) e a maior concordância entre períodos consecutivos (ARI médio de 0,78) |

A silhueta em torno de 0,37 indica estrutura **moderada**: os mercados formam mais um gradiente de preço do que blocos bem separados. Por isso a conclusão também se apoia na ordem dos mercados, que não depende do K-Means (seção 6).

Os grupos são renumerados do mais barato (0) ao mais caro (`q3_clustering.ordenar_grupos`), para os rótulos serem comparáveis entre execuções e entre períodos.

---

## 5. Economia em R$: Cesta Básica do DIEESE

**Decisão:** a diferença de preço vira reais com as quantidades mensais da **Cesta Básica do DIEESE, Região 1**, que inclui São Paulo (`config.CESTA_DIEESE`).

**Por quê:** é a referência de "cesta básica" no Brasil, definida pelo Decreto-Lei 399/1938 (ainda em vigor) para sustentar um trabalhador adulto por um mês. Os 14 produtos do projeto são exatamente os 13 itens dessa cesta, com a banana em duas variedades. Para um trabalho de extensão, falar em "a cesta básica do DIEESE" é mais útil que uma cesta arbitrária.

**Fonte:** DIEESE, *Metodologia da Pesquisa Nacional da Cesta Básica de Alimentos*, agosto de 2025 (tabela "provisões mínimas estipuladas pelo Decreto Lei nº 399"; Região 1 = ES, MG, RJ, SP, GO e DF). A metodologia de janeiro de 2016 traz a mesma tabela.

| Item DIEESE (Região 1) | Quantidade/mês | Produto no projeto | Na unidade do PPK |
|---|---|---|---|
| Carne | 6,0 kg | Carne Bovina Coxão Mole | 6,0 kg |
| Leite | 7,5 L | Leite | 7,5 L |
| Feijão | 4,5 kg | Feijão | 4,5 kg |
| Arroz | 3,0 kg | Arroz | 3,0 kg |
| Farinha | 1,5 kg | Farinha de Trigo | 1,5 kg |
| Batata | 6,0 kg | Batata | 6,0 kg |
| Legumes (tomate) | 9,0 kg | Tomate | 9,0 kg |
| Pão francês | 6,0 kg | Pão Francês | 6,0 kg (fora da Q3) |
| Café em pó | 600 g | Café | 0,6 kg |
| Frutas (banana) | 90 unidades | Banana Prata / Banana Nanica | 4,5 kg / 6,75 kg |
| Açúcar | 3,0 kg | Açúcar | 3,0 kg |
| Banha/óleo | 750 g | Óleo | 0,815 L |
| Manteiga | 750 g | Manteiga | 0,75 kg |

**Conversões e premissas:**
- **Banana:** 90 unidades = 7,5 dúzias. Segundo a própria metodologia, o DIEESE converte o preço do quilo em preço da dúzia multiplicando por **1,2 na prata e 1,8 na nanica**, ou seja, uma dúzia pesa cerca de 1,2 kg e 1,8 kg. O documento não diz como as duas variedades são combinadas. **Premissa nossa:** metade das dúzias de cada, o que dá 3,75 dz × 1,2 = 4,5 kg de prata e 3,75 dz × 1,8 = 6,75 kg de nanica.
- **Óleo:** o DIEESE usa 750 g, e o PPK do óleo está em R$/litro (embalagem de 900 ml). A conversão usa a densidade aproximada do óleo de soja, 0,92 kg/L: 0,75 ÷ 0,92 ≈ 0,815 L. O óleo é cerca de 1% da cesta, então o erro da aproximação é desprezível.
- **Carne:** o DIEESE pesquisa coxão mole, coxão duro e patinho. A base só tem coxão mole, que representa a carne.
- **Preço de hoje:** o preço de cada produto é a média do preço geral nos últimos 12 meses da base, set/2025 a ago/2026 (`config.MESES_PRECO_CESTA`).
- **Perfil de cada grupo:** média do preço relativo dos seus mercados em cada produto.
- **Premissa principal:** o preço relativo típico de cada mercado, a mediana de 48 meses, continua valendo para os preços de hoje. A estabilidade da seção 6 sustenta essa premissa.

---

## 6. Estabilidade no tempo

**Decisão:** o agrupamento é refeito em 4 períodos de 12 meses, de setembro a agosto (`config.PERIODOS_ESTABILIDADE`), e comparado com o do período completo e com o período anterior.

**Por que esses períodos:** 12 meses cobrem um ciclo inteiro de safra do hortifrúti, e começar em setembro usa os 48 meses sem sobra. Os 25 mercados aparecem nos 4 períodos, e nenhum mercado fica sem algum produto num período.

**Medidas:**
- **ARI** (adjusted Rand index): 1 = mesmos grupos, ~0 = concordância de acaso. Não depende da numeração dos grupos.
- **% no mesmo grupo:** com os grupos ordenados do mais barato ao mais caro.
- **Correlação de Spearman do índice de preço:** compara a ordem dos mercados, do mais barato ao mais caro. Não depende do K-Means.

**Limitação:** os meses que faltam nos 25 mercados se concentram a partir de ago/2025 (decisão 4). O último período se apoia em menos meses por mercado (no mínimo 3 numa célula).

---

## 7. Resultado (notebook 05)

- **Grupo 0, mais baratos:** 10 mercados, preço 9% abaixo da mediana (índice 0,91) e mais baratos em **todos os 13 produtos**.
- **Grupo 1, intermediários:** 11 mercados, índice 1,06, mais caros sobretudo nos industrializados (farinha +12%, açúcar +9%, leite, óleo e feijão +8%).
- **Grupo 2, mais caros:** 4 mercados, índice 1,12, caros sobretudo no hortifrúti (batata +38%, banana nanica +37%, banana prata +21%, tomate +20%).
- **Estabilidade:** 9 dos 10 mercados do grupo barato ficam nele nos 4 períodos; só o SUP_17, na fronteira (índice 0,96), oscila. A correlação de Spearman entre a ordem de cada período e a do período completo fica entre 0,96 e 0,99.
- **Economia** (cesta DIEESE sem pão, preços de set/2025 a ago/2026):

| | Custo da cesta por mês |
|---|---|
| Grupo mais barato | R$ 664,53 |
| Mediana entre mercados | R$ 736,01 |
| Grupo mais caro | R$ 838,30 |
| Mercado mais barato (SUP_46) | R$ 633,91 |
| Mercado mais caro (SUP_16) | R$ 859,01 |

Comprar no grupo mais barato economiza **R$ 71,48 por mês (9,7%)** em relação à mediana e **R$ 173,77 por mês (cerca de R$ 2.085 por ano)** em relação ao grupo mais caro.

---

## 8. Limitações

- **Marca e qualidade:** o preço do mercado é a mediana das marcas que ele vende. Parte do "barato" pode vir de marcas mais baratas, e não só de cobrar menos pelo mesmo item.
- **Custos fora da conta:** deslocamento, compra em volume (atacarejo) e tempo não entram na economia calculada.
- **Gradiente, não blocos:** os grupos resumem um gradiente de preço. A conclusão "há mercados consistentemente baratos" vale também pela estabilidade da ordem, sem depender do K-Means.
- **Anonimização:** o trabalho mostra que esses mercados existem e quanto valem, mas não quais são.
