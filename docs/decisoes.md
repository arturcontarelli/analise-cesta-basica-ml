# Decisões do projeto

Este arquivo registra **o que** foi decidido e **por quê**, para que qualquer integrante do grupo entenda as escolhas antes de mexer no código. Se uma decisão mudar, atualize aqui com a data e o motivo; não apague a anterior, risque ou marque como substituída.

Última revisão: 23/11/2026

---

## 1. Questões estudadas: Q1 + Q3

**Decisão:** o trabalho responde duas questões:
- **Q1:** é possível prever o preço do mês seguinte de cada produto melhor do que simplesmente repetir o preço atual?
- **Q3:** existem mercados consistentemente mais baratos? Quanto o consumidor economiza escolhendo bem onde comprar?

**Por quê:**
- O enunciado exige ao menos 1 questão com Questão, Objetivo/Motivação, Método e Conclusão. Duas questões dão margem de segurança.
- Q1 usa **aprendizado supervisionado** (aulas 08, 09, 10) e Q3 usa **aprendizado não-supervisionado** (aulas 11, 12). Juntas cobrem as duas metades da disciplina.
- Cada questão tem um problema real por trás, o que importa por ser um trabalho de **extensão**:
  - Q1: ONGs, bancos de alimentos, prefeituras e famílias planejam orçamento com antecedência; saber quanto a cesta deve custar no mês seguinte ajuda nesse planejamento.
  - Q3: o consumidor não sabe quais mercados são baratos de forma consistente, e pesquisar preço toda semana custa tempo e transporte.

**Alternativa descartada — Q2 (classificar se o preço sobe ou desce) como questão separada:** a Q1 já responde isso implicitamente. Se o modelo prevê o preço do mês seguinte, basta comparar com o preço atual para saber se prevê alta ou queda. Por isso a Q1 é avaliada também como classificação de direção (ver decisão 7), sem precisar de um modelo extra.

---

## 2. Produtos analisados

**Decisão:** 14 produtos, usados nas duas questões:
Café, Arroz, Feijão, Leite, Manteiga, Farinha de Trigo, Óleo, Açúcar, Tomate, Batata, Banana Prata, Banana Nanica, Carne Bovina Coxão Mole, Pão Francês. Macarrão com Ovos entra se sobreviver à limpeza.

**Por quê:**
- São os produtos com cerca de 1.000 registros ou mais na base (os 8 primeiros têm entre 3 e 5 mil).
- Cobrem a cesta de forma representativa: grãos, laticínios, hortifruti, carne e pão. Isso torna o resultado mais útil para a comunidade.
- Como a Q1 usa a mediana entre mercados (decisão 3), mesmo os produtos com menos dados ficam com séries mensais aproveitáveis.

**Ficaram de fora:** ovo, frango (peito e sobrecoxa), acém, pernil e outros cortes, todos com menos de 500 registros, o que geraria séries com muitos buracos.

**Observação:** Macarrão com Ovos provavelmente sai, porque nenhum mercado tem série longa dele (a coleta parece ter começado tarde).

**Limpeza obrigatória de nomes:** a base tem nomes duplicados para o mesmo produto ("Pão" e "Pão Francês", "Farinha" e "Farinha de Trigo", "Macarrão" e "Macarrão com Ovos" etc.). Eles devem ser unificados antes de qualquer análise, e o mapeamento fica em `src/config.py`.

---

## 3. Q1 usa o preço GERAL (mediana entre mercados)

**Decisão:** para cada produto e mês, o preço da Q1 é a **mediana do PPK** (preço por kg/unidade) entre todos os mercados pesquisados naquele mês.

**Por quê:**
- **Reduz o ruído.** A série de um mercado sozinho oscila por motivos que não têm a ver com a tendência real do preço: promoção num mês, marca diferente coletada, uma única coleta num dia atípico. Na mediana de ~27 mercados esses efeitos se cancelam e sobra o movimento real (inflação, safra, alta de um insumo), que é o que dá para prever.
- **Usa mais dados.** A mediana aproveita os 51 mercados; a previsão por mercado só aproveitaria os ~25 com séries quase completas.
- **Mediana em vez de média:** a mediana é menos afetada por valores extremos (uma promoção muito agressiva ou um erro de digitação).
- **PPK em vez de Preço:** os produtos vêm em embalagens de tamanhos diferentes; o PPK torna os preços comparáveis.

**Alternativa descartada — prever por mercado:** séries mais curtas e ruidosas, previsões menos confiáveis. A comparação entre mercados não se perde, porque fica na Q3.

---

## 4. Q3 usa os dados POR MERCADO

**Decisão:** a Q3 analisa cada mercado separadamente, usando apenas os mercados com séries quase completas (cerca de 40 dos 48 meses ou mais, o que dá ~25 dos 51 mercados).

**Por quê:**
- Comparar mercados é o objetivo da Q3; não faz sentido agregar.
- Dos 51 mercados, muitos entram e saem da pesquisa (em média só ~27 são coletados por mês). Mercados com poucos meses não permitem dizer se são baratos **de forma consistente**.
- O limite exato de meses fica em `src/config.py` e deve ser justificado na exploração (gráfico de meses disponíveis por mercado).

**Método:** cada mercado é representado pelo seu preço relativo em cada produto (acima ou abaixo da mediana geral). Usa-se K-Means, com k escolhido por cotovelo, silhueta e índice Xie-Beni (aulas 11 e 12). Avalia-se também se os grupos se mantêm estáveis no tempo: se o mercado barato de 2023 virou caro em 2025, a recomendação não se sustenta.

**Atualização 23/11/2026 — corte fixado em 40 meses (notebook 02):** depois da limpeza (decisão 10), há um vão natural na contagem de meses por mercado: 25 mercados têm de 41 a 48 meses e o próximo tem 34 (depois 31, 28, 18, 14, e 21 estabelecimentos com 1 a 3 meses). Como nenhum mercado tem de 35 a 40 meses, **qualquer corte entre 35 e 41 seleciona os mesmos 25 mercados**, então o resultado não depende do valor exato. Os meses que faltam nesses 25 mercados se concentram a partir de ago/2025 (pior mês: fev/2026, com 13 dos 25 ausentes), o que deve ser considerado ao medir a estabilidade dos grupos no tempo. Gráficos: `reports/figures/02_meses_por_mercado.png` e `02_presenca_mercados.png`.

**Limitação conhecida:** os mercados são anonimizados (SUP_01...). O trabalho mostra **se existem** mercados consistentemente baratos e **quanto isso vale em R$**, mas não diz qual é cada um.

---

## 5. Custo do produtor (CONAB) como variável extra na Q1

**Decisão:** usar as planilhas de custo de produção da CONAB como informação extra na Q1, **apenas para Arroz, Feijão, Café e Leite**.

**O que é:** o enunciado sugere comparar o preço do mercado com o "preço do produtor" e indica o link do site da CONAB (Companhia Nacional de Abastecimento, órgão federal). Lá estão planilhas com quanto o agricultor gasta para produzir cada cultura (sementes, adubo, diesel, mão de obra etc.). A hipótese é que um aumento no custo do produtor chega ao preço do mercado alguns meses depois, então ele pode ajudar a prever.

**Por que só esses 4:**
- Têm muitos dados na base do professor.
- São produtos agrícolas "brutos", com ligação direta ao custo do agricultor. Produtos industrializados (pão, manteiga, óleo, macarrão) não têm planilha direta.
- Limitar reduz o trabalho de baixar e alinhar outra base.

**Riscos (verificar antes de usar):**
- **Frequência:** os custos provavelmente são calculados por safra (1 ou 2 vezes por ano), não por mês. Seria preciso repetir ou interpolar os valores, e isso precisa ser justificado.
- **Região:** os custos são por região produtora; é preciso escolher uma região representativa (de preferência São Paulo ou o estado produtor mais próximo) e usar a mesma para todos os produtos.
- **Unidade:** pode vir em R$/hectare ou R$/saca; conferir antes de usar.

**Procedimento:** baixar primeiro um único arquivo (feijão) e checar frequência, região e unidade. Se não for possível alinhar com os dados mensais, a CONAB é descartada e o descarte é justificado no relatório (isso também conta como rigor metodológico).

---

## 6. Modelos

**Q1 — modelos das aulas (obrigatórios):**
- **Baseline ingênuo:** o preço do mês seguinte é igual ao do mês atual. Serve de régua: se um modelo não erra menos que isso, ele não aprendeu nada útil.
- **Regressão linear** (aula 09): usa os preços dos meses anteriores (lags) como entrada.
- **KNN regressor** (aula 08): prevê pela média dos meses passados mais parecidos.
- **Ensemble** (aula 10): média ponderada dos modelos acima (peso = 1 / erro de validação). Descartado stacking: com ~30 meses de treino por produto, um meta-modelo teria poucos exemplos para aprender uma combinação confiável.

**Q1 — modelo extra, decidido em 23/11/2026: Random Forest** (bagging de árvores; bagging é citado na aula 10).
- O enunciado incentiva "estudar e aprender outros modelos", mas um modelo extra **não é necessário** para responder a questão.
- Ele faz sentido se os modelos da aula não forem suficientes. Por exemplo, a regressão linear só capta relações em linha reta, e a relação entre custo do produtor e preço pode não ser linear.
- Regra: rodar primeiro os modelos da aula. Se já baterem o baseline com folga, o extra entra só como comparação ("testamos um modelo mais complexo e ele não melhorou", que também é conclusão). Se nenhum bater o baseline, o extra ajuda a descobrir se o problema é o modelo simples demais ou se os dados realmente não permitem prever. Princípio: **adicionar complexidade só quando os dados mostrarem necessidade.**
- **Gatilho da decisão:** nem o ensemble bateu o baseline com folga (venceu em só 3 dos 14 produtos), então pela regra acima o extra virou necessário.
- **Hiperparâmetros fixos** (não escolhidos por validação como o k do KNN): `max_depth=4`, `min_samples_leaf=2`, para não decorar o treino com só ~30 meses por produto.
- **Resultado:** a Random Forest bateu o baseline em 3 dos 14 produtos (Banana Nanica, Manteiga, Óleo) — taxa parecida com a do ensemble, não uma melhora clara. Isso aponta para "o preço é difícil de prever com este histórico" mais do que para "os modelos simples eram fracos demais".
- **Limitação conhecida:** Random Forest não extrapola além do maior preço visto no treino (previsão é uma média de valores de treino). Em produtos com tendência de alta, isso tende a subestimar o preço do teste por motivo estrutural, não por falta de padrão — ver diagnóstico de extrapolação no notebook 04.
- **Comparação informal (não é modelo oficial):** testamos também Gradient Boosting, só para checar se boosting supera o bagging aqui. Resultado: pior que a Random Forest em 11 dos 14 produtos. Com poucos meses de treino por produto, o ajuste mais fino do boosting não compensou.

**Q3:** K-Means (aula 11). Não precisa de modelo extra.

---

## 7. Avaliação

**Decisão:** toda avaliação da Q1 usa **divisão temporal**: treinar com os meses mais antigos e testar com os mais recentes (por exemplo, treinar até o mês 36 e testar nos meses 37 a 48), ou uma janela que avança mês a mês (walk-forward).

**Por quê:**
- O k-fold ensinado na aula 10 embaralha os dados. Em série temporal isso faz o modelo treinar com meses **futuros** para prever meses **passados**, o que é exatamente o vazamento do teste que a aula 10 (slide 25) proíbe. O resultado ficaria artificialmente bom.
- Hiperparâmetros (como o k do KNN ou quantos meses de lag usar) são escolhidos numa parte separada do treino, nunca olhando o teste (aula 10, slide 26).

**Métricas da Q1:**
- **Erro em valor:** MAE e MSE (aulas 09 e 10). Respondem "quanto vou gastar?".
- **Acerto de direção:** cada previsão vira "sobe / não sobe" comparando com o preço atual; calcula-se matriz de confusão, acurácia, precisão e revocação (aula 10). Respondem "compro agora ou espero?".
- As duas são reportadas separadamente, porque acertar o valor e acertar a direção não são a mesma coisa: o modelo pode errar só R$ 0,05 e ainda assim errar a direção.

**Métricas da Q3:** cotovelo, silhueta e Xie-Beni para escolher k e avaliar os grupos (aulas 11 e 12), economia em R$ entre grupos e estabilidade dos grupos no tempo.

**Conclusão negativa também é resultado:** com só 48 meses, é possível que nenhum modelo bata o baseline. Se acontecer, a conclusão é que o preço desses itens é praticamente imprevisível no curto prazo e a melhor estimativa disponível é o preço atual. Isso deve ser reportado com justificativa, não escondido.

---

## 8. Ferramentas e organização

**Decisão:** Python, com pandas, numpy, scikit-learn, matplotlib e seaborn, em notebooks numerados (`01_limpeza`, `02_exploracao`...) que usam funções de `src/`.

**Por quê:**
- **Python:** linguagem pedida pelo professor em aula (o enunciado escrito não especifica) e com as bibliotecas de ML mais usadas.
- **Notebooks numerados:** deixam clara a ordem de execução, e cada etapa pode ter um responsável.
- **Lógica em `src/` em vez de dentro dos notebooks:** evita copiar e colar o mesmo código entre notebooks e garante que todos usem a mesma limpeza e a mesma avaliação.
- **`src/config.py` como fonte única** da lista de produtos, nomes duplicados e caminhos: se uma decisão mudar, muda em um lugar só.
- **Dados originais em `data/raw/` e nunca editados:** qualquer pessoa consegue refazer tudo do zero. Os dados gerados vão para `data/processed/`.
- **Os dados ficam no repositório:** o enunciado exige entregar "código fonte e demais bases de dados utilizadas".

---

## 9. Formato da série geral: tabela longa

**Decisão:** `aggregation.serie_geral` (parte A) devolve uma tabela no formato **longo**, com colunas `produto`, `mes`, `preco` e `n_mercados` (uma linha por combinação produto/mês), e não uma tabela larga (um produto por coluna).

**Por quê:**
- A Q1 (parte C) percorre os produtos em loop (`config.PRODUTOS`) para montar lags e treinar um modelo por produto; no formato longo isso é só `df[df.produto == produto]`, sem precisar de `pivot`.
- Facilita juntar depois as variáveis da CONAB (decisão 5), que também vêm como série por período — concatenar duas tabelas longas por `mes` é mais direto do que alinhar colunas largas.
- `n_mercados` (quantos mercados entraram na mediana daquele mês) é útil na exploração (notebook 02) e fica natural como mais uma coluna no formato longo.

**Combinar com quem for implementar `aggregation.py`:** este é o contrato de dados entre a parte A e a parte C — se o formato mudar, as duas partes precisam ser avisadas.

---

## 10. Critérios de limpeza da base de preços (parte A)

**Decisão:** além de unificar nomes e filtrar os 14 produtos (decisão 2), a limpeza (`src/cleaning.py`, notebook 01):
1. **remove linhas duplicadas** (idênticas em mercado, dia, produto, marca, preço e quantidade), mantendo uma cópia;
2. **mantém só a embalagem padrão** de cada produto (`config.EMBALAGEM_PADRAO`: a quantidade mais comum, ex.: manteiga 200 g, café 500 g, arroz 5 kg, óleo 900 ml);
3. **remove preços atípicos:** PPK mais de 3× acima ou abaixo da mediana do mesmo produto no mesmo mês (`config.FATOR_PRECO_ATIPICO`).

E o preço geral da Q1 (decisão 3) é calculado em **duas etapas**: primeiro a mediana de cada mercado no mês, depois a mediana entre os mercados.

**Resultado:** de 42.940 linhas dos 14 produtos, ficam 41.029 (95,6%). Saem 1.682 duplicatas, 195 embalagens fora do padrão e 34 preços atípicos (tabela em `reports/tables/limpeza_resumo.csv`). A série geral fica com 14 produtos × 48 meses, sem mês vazio, com ~27 mercados por mediana.

**Por quê:**
- **Duplicatas:** uma mesma coleta registrada duas vezes faria o preço contar em dobro na mediana do mercado. Ex. real: manteiga no SUP_51 em fev/2025 tinha R$ 59,95, R$ 59,95, R$ 99,95 e R$ 99,95 (duplicata); a mediana caía de R$ 79,95 para R$ 59,95 sem a cópia. O efeito no preço geral é pequeno (11 de 672 valores mudam, no máximo 5%), mas na comparação entre mercados (Q3) distorce. Linhas da mesma marca com preço ou dia diferente **não** são removidas: são versões diferentes do produto (ex.: arroz tipo 1 e parboilizado) ou visitas diferentes no mês.
- **Embalagem padrão:** cobre ~99% dos registros e garante que se compara sempre o mesmo item. Na manteiga, 97% é pote de 200 g; os potes de 250/500 g têm PPK bem menor e muitos são margarina (Qualy, Claybom, Doriana). Também elimina quantidades digitadas erradas (tomate com quantidade 20, manteiga com quantidade 3), que geram PPK errado mesmo com o preço certo.
- **Preços atípicos com fator 3, comparando com o mesmo mês:** pega os valores impossíveis (banana a R$ 999/kg, pão e coxão mole a R$ 0,10/kg, arroz de 5 kg registrado com o preço do kg, manteiga de 200 g a R$ 3–4). Comparar com o mesmo mês evita confundir inflação ou safra com erro. Um fator 2 removeria 242 linhas; um fator 3,5 removeria 17, mas manteria erros claros (arroz e manteiga com razão de 0,30 a 0,32 da mediana).
- **Mediana em duas etapas:** um mercado pode ter 8 marcas de arroz num mês e outro só 1. Na mediana direta, o primeiro pesaria 8 vezes mais. Em duas etapas, cada mercado vale um voto, que é o que a decisão 3 pretende ("mediana entre mercados"), e `n_mercados` conta mercados de verdade.

**Alternativas descartadas:** regra do IQR por produto (sensível em meses com poucos registros); manter todas as embalagens (mistura manteiga com margarina); mediana direta de todos os registros (dá peso maior a mercados com mais marcas).

**Limitações:**
- A base não tem coluna de "versão do produto": duas versões da mesma marca com o mesmo preço, no mesmo dia, são indistinguíveis de uma duplicata e uma delas é removida. O efeito na mediana é desprezível.
- O fator 3 também remove ~10 preços baixos de hortifrúti (banana a R$ 1,99–2,99, batata a R$ 1,95, tomate a R$ 2,99) que podem ser promoções reais, porque estão na mesma faixa (≈ 1/3 da mediana) dos erros de arroz e manteiga. Não há limite único que separe os dois grupos. O efeito na mediana entre mercados é desprezível; na Q3, esses mercados perdem alguns meses de promoção.
- `Data_Coleta` está vazia de nov/2025 em diante. Nesse período, duas visitas no mesmo mês com o mesmo preço também parecem duplicata.
- 5 dos 51 estabelecimentos (`ALT_26`, `ALT_28`, `ALT_35`, `ALT_48`, `ALT_49`) aparecem em um único mês cada. Ficam na Q1 (são coletas reais) e saem da Q3 pelo mínimo de meses (decisão 4).
