// Relatório de extensão — Análise e previsão de preços da cesta básica
// Template ABNT (NBR 14724) escrito à mão em Typst, sem dependências externas.

#let instituicao = "PONTIFÍCIA UNIVERSIDADE CATÓLICA DE CAMPINAS"
#let curso = "Engenharia de Computação"
#let disciplina = "Sistemas Inteligentes e Aprendizado de Máquina (13134)"
#let professor = "Fernando S. de Aguiar Neto"
#let titulo = "ANÁLISE E PREVISÃO DE PREÇOS DA CESTA BÁSICA"
#let subtitulo = "um estudo com aprendizado supervisionado e não supervisionado"
#let autores = ("Artur Contarelli", "Guilerme Eid", "Lucas Sabino", "Tiago Rodrigues")
#let cidade = "Campinas"
#let ano = "2026"

#set document(title: titulo, author: autores)

// ---------------------------------------------------------------------------
// Configuração geral (NBR 14724): A4, margens 3/2/3/2 cm, fonte 12pt, 1,5 espaço
// ---------------------------------------------------------------------------
#set page(
  paper: "a4",
  margin: (left: 3cm, right: 2cm, top: 3cm, bottom: 2cm),
  numbering: none,
)
#set text(
  font: ("Times New Roman", "Liberation Serif", "New Computer Modern"),
  size: 12pt,
  lang: "pt",
  region: "BR",
)
#set par(justify: true, leading: 1em, first-line-indent: 1.25cm)
#set heading(numbering: "1.1.1")

// Legendas de figura/tabela em português, sem ponto final, fonte menor
#set figure.caption(separator: [ — ])
#show figure.caption: it => text(size: 10pt, it)
#show figure: set block(breakable: false)

// Títulos de seção numerada (textual): negrito, maiúsculo, alinhado à esquerda
#show heading.where(level: 1, numbering: "1.1.1"): it => {
  pagebreak(weak: true)
  v(0.4cm)
  set par(first-line-indent: 0cm)
  set text(weight: "bold", size: 12pt)
  block(upper[#counter(heading).display() #h(0.3cm) #it.body])
  v(0.3cm)
}
#show heading.where(level: 2): it => {
  v(0.5cm)
  set par(first-line-indent: 0cm)
  set text(weight: "bold", size: 12pt)
  block[#counter(heading).display() #h(0.3cm) #it.body]
  v(0.2cm)
}
#show heading.where(level: 3): it => {
  v(0.4cm)
  set par(first-line-indent: 0cm)
  set text(weight: "bold", style: "italic", size: 12pt)
  block[#counter(heading).display() #h(0.3cm) #it.body]
  v(0.15cm)
}

// Títulos pré/pós-textuais sem numeração: negrito, maiúsculo, centralizado
#let titulo-sem-numero(corpo) = heading(level: 1, numbering: none, outlined: true, corpo)
#show heading.where(level: 1, numbering: none): it => {
  pagebreak(weak: true)
  v(0.4cm)
  set par(first-line-indent: 0cm)
  set align(center)
  set text(weight: "bold", size: 12pt)
  block(upper(it.body))
  v(0.3cm)
}

// ---------------------------------------------------------------------------
// Elementos textuais pré-textuais
// ---------------------------------------------------------------------------

// CAPA
#[
  #set align(center)
  #set par(first-line-indent: 0cm)
  #text(weight: "bold")[#instituicao]
  #v(0.3cm)
  #text()[#curso]
  #v(1fr)
  #for a in autores [#a \ ]
  #v(1fr)
]

// FOLHA DE ROSTO
#[
  #set align(center)
  #set par(first-line-indent: 0cm)

  #v(1fr)
  #block(width: 80%)[
    #text(weight: "bold", size: 14pt)[#upper(titulo)] \
    #v(0.2cm)
    #text(size: 12pt)[#subtitulo]
  ]
  #v(1fr)
  #block(width: 50%, below: 0pt)[
    #set align(left)
    #set par(justify: true, first-line-indent: 0cm, leading: 0.65em)
    #set text(size: 11pt)
    Relatório de extensão apresentado à disciplina #disciplina, do curso de graduação em #curso da #instituicao, como parte das atividades de extensão universitária, sob orientação do Prof. #professor.
  ]
  #v(1fr)
  #cidade \
  #ano
]

// RESUMO
#titulo-sem-numero[Resumo]
#set par(first-line-indent: 0cm)
Este trabalho de extensão utiliza dados reais de preços de itens da cesta básica, coletados em 51 supermercados anonimizados entre setembro de 2022 e agosto de 2026, para gerar conhecimento útil a organizações e famílias que planejam o orçamento alimentar. Duas questões são investigadas. A primeira (Q1), de aprendizado supervisionado, avalia se é possível prever o preço do mês seguinte de 14 produtos melhor do que simplesmente repetir o preço atual, comparando um baseline ingênuo, regressão linear, KNN, um ensemble ponderado e, como modelo extra, Random Forest — com Gradient Boosting testado apenas para comparação informal —, avaliados por divisão temporal com métricas de erro (MAE, MSE) e de acerto de direção (acurácia, precisão, revocação). A segunda questão (Q3), de aprendizado não supervisionado, investiga se existem mercados consistentemente mais baratos entre os 25 estabelecimentos com cobertura temporal suficiente, por meio de agrupamento com K-Means sobre o preço relativo de 13 produtos, com $k$ escolhido por cotovelo, silhueta e índice Xie-Beni, e estimativa da economia em reais usando a Cesta Básica do DIEESE. Os resultados da Q1 mostram que, dos modelos avaliados, a regressão linear é a que mais se aproxima do baseline, batendo-o em 6 dos 14 produtos, mas nenhuma abordagem o supera de forma consistente — uma conclusão negativa válida diante de um histórico de apenas 48 meses. Os resultados da Q3 identificam três grupos de mercados estáveis ao longo do tempo (índice Rand ajustado acima de 0,67 em todos os períodos testados) e mostram que escolher o grupo mais barato economiza R\$ 71,48 por mês (9,7%) em relação à mediana entre mercados e R\$ 173,77 por mês (cerca de R\$ 2.085 por ano) em relação ao grupo mais caro.

#v(0.5cm)
*Palavras-chave*: Cesta básica. Aprendizado de máquina. Séries temporais. Agrupamento. K-Means.

// ABSTRACT
#set text(lang: "pt", region: "BR")

// SUMÁRIO
#titulo-sem-numero[Sumário]
#set par(first-line-indent: 0cm)
#outline(title: none, indent: auto)

// LISTA DE ILUSTRAÇÕES
#titulo-sem-numero[Lista de ilustrações]
#set par(first-line-indent: 0cm)
#outline(title: none, target: figure.where(kind: image))

// LISTA DE TABELAS
#titulo-sem-numero[Lista de tabelas]
#set par(first-line-indent: 0cm)
#outline(title: none, target: figure.where(kind: table))

// ---------------------------------------------------------------------------
// Elementos textuais: a partir daqui a paginação aparece (NBR 14724)
// ---------------------------------------------------------------------------
#set page(numbering: "1", number-align: top + right)
#counter(page).update(1)
#set par(first-line-indent: 1.25cm)

= Introdução

A cesta básica reúne os itens de alimentação considerados essenciais para a subsistência de um trabalhador e de sua família, e o acompanhamento de seu preço é uma referência direta do custo de vida no Brasil. Este relatório descreve um trabalho de extensão da disciplina #disciplina, da #instituicao, que usa dados reais de preços coletados em 51 supermercados (identificados apenas por código, para preservar o anonimato) entre setembro de 2022 e agosto de 2026, cobrindo 14 produtos da cesta básica: café, arroz, feijão, leite, manteiga, farinha de trigo, óleo, açúcar, tomate, batata, banana prata, banana nanica, carne bovina (coxão mole) e pão francês.

Por se tratar de um trabalho de extensão, o objetivo não é apenas acadêmico: os resultados pretendem ser úteis a quem de fato lida com o custo da cesta básica no dia a dia — ONGs, bancos de alimentos e prefeituras que planejam doações e políticas com antecedência, famílias que organizam o orçamento mensal, e consumidores que não sabem quais mercados são baratos de forma consistente e gastam tempo e deslocamento pesquisando preço. Para isso, o trabalho responde a duas questões, uma de aprendizado supervisionado e outra de aprendizado não supervisionado, descritas na seção 2 e detalhadas na metodologia (seção 3) e nos resultados (seção 4).

O trabalho foi dividido em quatro partes entre os integrantes do grupo: limpeza e exploração da base, leitura e tratamento dos dados de custo de produção da Companhia Nacional de Abastecimento (CONAB), a questão de previsão de preços (Q1) e a questão de agrupamento de mercados (Q3). Essa organização é refletida na estrutura da metodologia e dos resultados a seguir.

= Objetivo e motivação

== Questão 1 — previsão de preços (aprendizado supervisionado)

*Questão*: dado o histórico de preços de um produto, é possível prever o seu preço no mês seguinte melhor do que simplesmente repetir o preço do mês atual?

*Objetivo e motivação*: uma previsão de preço minimamente confiável tem aplicação direta no planejamento de orçamento com antecedência. ONGs, bancos de alimentos, prefeituras e famílias que sabem, com alguma margem de erro, quanto a cesta deve custar no mês seguinte podem reservar recursos de forma mais realista do que assumindo que o preço simplesmente não muda. O conhecimento esperado é tanto o valor previsto do preço (quanto vai custar) quanto a direção da variação (vai subir ou não), que respondem perguntas complementares de planejamento e de decisão de compra.

== Questão 3 — agrupamento de mercados (aprendizado não supervisionado)

*Questão*: existem mercados consistentemente mais baratos do que outros? Quanto o consumidor economiza escolhendo bem onde comprar?

*Objetivo e motivação*: o consumidor comum não sabe, de forma sistemática, quais estabelecimentos são baratos de forma consistente ao longo do tempo — e pesquisar preço em vários mercados toda semana custa tempo e deslocamento. Se existirem grupos de mercados consistentemente mais baratos, essa informação tem valor direto para quem decide onde fazer as compras. O conhecimento esperado é tanto a existência (ou não) de tais grupos quanto a quantificação, em reais, do quanto vale a pena escolher bem o mercado.

= Metodologia

== Base de dados e limpeza

A base original contém 46.264 registros de coleta de preço, por mercado, produto, marca e dia. Os 14 produtos analisados foram escolhidos por reunirem a maior quantidade de registros (acima de mil cada, frente a itens com menos de 500 registros, como ovo e frango, descartados por gerarem séries com muitos meses vazios) e por cobrirem a cesta de forma representativa — grãos, laticínios, hortifrúti, carne e pão —, o que torna o resultado mais útil à comunidade.

Antes de qualquer análise, nomes duplicados do mesmo produto na base (por exemplo, "Pão" e "Pão Francês", "Farinha" e "Farinha de Trigo") foram unificados, e a limpeza aplicou três critérios, nessa ordem: remoção de linhas duplicadas (idênticas em mercado, dia, produto, marca, preço e quantidade); manutenção apenas da embalagem padrão de cada produto (a quantidade mais comum, por exemplo manteiga de 200 g e arroz de 5 kg), para não misturar itens diferentes nem quantidades digitadas de forma errada; e remoção de preços atípicos, definidos como preço por kg/unidade (PPK) mais de três vezes acima ou abaixo da mediana do mesmo produto no mesmo mês, o que evita confundir inflação ou sazonalidade de safra com erro de digitação. O resultado está na @tab-limpeza.

#figure(
  caption: [Resultado da limpeza da base de preços],
  table(
    columns: 3,
    stroke: none,
    align: (left, right, right),
    table.hline(),
    table.header([*Etapa*], [*Linhas*], [*Removidas*]),
    table.hline(stroke: 0.5pt),
    [Base original (14 produtos)], [42.940], [—],
    [Remover duplicatas], [41.258], [1.682],
    [Filtrar embalagem padrão], [41.063], [195],
    [Remover preços atípicos], [41.029], [34],
    table.hline(),
  )
) <tab-limpeza>

Da base limpa, 41.029 de 42.940 linhas dos 14 produtos foram mantidas (95,6%). Para a questão de previsão (Q1), cada produto e mês recebe um único preço "geral": primeiro calcula-se a mediana do PPK de cada mercado no mês, depois a mediana entre os mercados, o que reduz o ruído de promoções e erros isolados e aproveita os 51 estabelecimentos. Para a questão de agrupamento (Q3), usam-se os 25 mercados com cobertura de ao menos 40 dos 48 meses da série, pois comparar mercados exige que a comparação seja sustentada por tempo suficiente de coleta — o corte exato entre 35 e 41 meses não altera a seleção, dado que não há nenhum mercado nessa faixa.

== Questão 1 — previsão de preços

A série usada é mensal, com um preço por produto e por mês (o preço "geral" descrito acima), entre setembro de 2022 e agosto de 2026 — 48 meses por produto. Cada observação recebe como entrada os preços dos $n$ meses anteriores (os *lags*) e como alvo o preço do mês seguinte; o número de lags é um ajuste escolhido por validação, não fixado a priori.

A avaliação segue sempre a divisão temporal, nunca validação cruzada embaralhada: treina-se com os meses mais antigos e testa-se nos meses mais recentes, pois embaralhar a série permitiria ao modelo "ver o futuro" para prever o passado, o que infla artificialmente o desempenho. Todos os 14 produtos são testados exatamente nos mesmos 11 meses (setembro de 2025 a julho de 2026); o treino, de 31 a 36 meses conforme o produto, termina sempre no mesmo mês. Os ajustes internos de cada modelo (o número de lags e, no KNN, o número de vizinhos) são escolhidos numa fatia de validação reservada dentro do próprio período de treino, sem nunca olhar o período de teste.

Cinco abordagens são comparadas para cada produto:

- *Baseline ingênuo*: o preço do mês seguinte é igual ao do mês atual. É a régua: qualquer abordagem mais elaborada só é considerada útil se bater esse palpite.
- *Regressão linear*: usa os lags como entrada numa relação linear com o preço seguinte.
- *KNN regressor*: prevê pela média dos meses passados com histórico mais parecido ao do momento atual.
- *Ensemble ponderado*: combinação dos três modelos acima por média ponderada, com peso proporcional ao inverso do erro de validação de cada um. Descartou-se o stacking, pois um meta-modelo teria poucos exemplos para aprender uma combinação confiável com apenas cerca de 30 meses de treino por produto.
- *Random Forest*: modelo extra, incluído porque nem o ensemble bateu o baseline com folga nos primeiros resultados, para avaliar se o problema estava nos modelos simples (lineares ou baseados em vizinhança) ou nos próprios dados. Os hiperparâmetros (`max_depth = 4`, `min_samples_leaf = 2`) foram fixados, e não escolhidos por validação, para não decorar o treino. Uma variante de boosting (*Gradient Boosting*) também foi testada apenas para comparação informal com a Random Forest, sem fazer parte da avaliação oficial.

Além do histórico de preços, para os quatro produtos com ligação mais direta à agricultura — arroz, feijão, café e leite — testou-se como variável extra uma estimativa do custo de produção, obtida nas planilhas de custo da CONAB. A hipótese é que um aumento no custo do produtor chegue, com atraso, ao preço de mercado. Essas séries, porém, têm frequência anual (não mensal), e o último valor conhecido precisou ser repetido (*forward-fill*) até o próximo relato, sem nunca preencher para trás, para não causar vazamento de informação futura. A comparação, em 11 meses de teste e 8 cenários (4 produtos × defasagem de 0 e 3 meses), mostrou que o melhor modelo com a variável da CONAB bate o baseline em apenas 1 dos 8 cenários (feijão, com defasagem de 3 meses), enquanto o melhor modelo sem ela bate em 2 dos 8 (leite); por não haver ganho consistente e por a cobertura ser desigual entre produtos, a variável da CONAB não entra nos modelos finais da Q1, permanecendo como evidência metodológica e em uma análise descritiva de arroz e feijão.

O desempenho de cada modelo é medido de duas formas, reportadas separadamente por não serem a mesma coisa: o *erro em valor* (MAE e MSE, "quanto vou gastar?") e o *acerto de direção* ("sobe"/"não sobe" em relação ao preço atual, avaliado por acurácia, precisão e revocação, "compro agora ou espero?"). Uma conclusão em que nenhum modelo bata o baseline de forma consistente é tratada como resultado válido, não como falha da análise: com apenas 48 meses de histórico, é plausível que o preço de alguns produtos seja de fato difícil de prever no curto prazo.

== Questão 3 — agrupamento de mercados

Cada um dos 25 mercados selecionados é descrito por seu *preço relativo* em cada um de 13 produtos (o pão francês foi excluído desta questão: 4 dos 25 mercados quase não vendem o produto, e são justamente os mais baratos nos demais itens — preencher o valor ausente os puxaria artificialmente para a média, e descartar esses mercados apagaria parte da própria resposta). O preço relativo é a razão entre o preço do mercado e o preço geral do mesmo produto no mesmo mês, resumida pela mediana ao longo do período; um valor de 1,10, por exemplo, significa 10% acima da mediana entre mercados. Nenhum valor é imputado. Diferente de práticas comuns em agrupamento, as 13 colunas não são padronizadas antes do K-Means, pois já estão na mesma unidade (proporção da mediana); padronizar daria à pequena diferença de preço do café (6%) o mesmo peso da diferença bem maior do hortifrúti (13% a 21%), distorcendo a distância entre mercados.

O número de grupos ($k$) foi escolhido testando valores de 2 a 8 por quatro critérios: o método do cotovelo e o índice Xie-Beni (que apontam $k=3$), a silhueta (praticamente empatada entre $k = 2$, $3$ e $4$, sem desempatar) e a estabilidade dos grupos ao longo de quatro períodos de 12 meses, na qual $k=3$ tem o melhor pior caso. Os grupos são renumerados do mais barato ao mais caro, para que os rótulos sejam comparáveis entre execuções e entre períodos.

A diferença de preço relativo entre grupos é convertida em economia mensal, em reais, usando as quantidades da Cesta Básica do DIEESE (Região 1, que inclui São Paulo), aos preços médios do produto nos últimos 12 meses da base (setembro de 2025 a agosto de 2026). A estabilidade dos grupos no tempo é verificada recalculando o agrupamento em quatro períodos de 12 meses (de setembro a agosto, o que cobre um ciclo completo de safra do hortifrúti) e comparando com o período completo e com o período anterior por três medidas: índice Rand ajustado (ARI, que não depende da numeração dos grupos), percentual de mercados no mesmo grupo e correlação de Spearman da ordem dos mercados do mais barato ao mais caro — esta última independente do próprio K-Means.

= Resultados e discussão

== Questão 1 — previsão de preços

A @tab-baseline resume, para os 14 produtos, quantas vezes cada modelo obteve um MAE menor que o do baseline ingênuo no período de teste.

#figure(
  caption: [Produtos em que cada modelo bate o baseline (MAE menor), de 14],
  table(
    columns: 3,
    stroke: none,
    align: (left, center, left),
    table.hline(),
    table.header([*Modelo*], [*Produtos*], [*Quais*]),
    table.hline(stroke: 0.5pt),
    [Regressão linear], [6 de 14], [Arroz, Banana Nanica, Batata, Farinha de Trigo, Manteiga, Tomate],
    [Random Forest], [5 de 14], [Arroz, Açúcar, Banana Nanica, Manteiga, Óleo],
    [Gradient Boosting (informal)], [5 de 14], [Açúcar, Banana Nanica, Batata, Manteiga, Óleo],
    [Ensemble ponderado], [4 de 14], [Banana Nanica, Batata, Manteiga, Óleo],
    [KNN], [3 de 14], [Banana Nanica, Batata, Manteiga],
    table.hline(),
  )
) <tab-baseline>

A regressão linear é a abordagem que mais se aproxima do baseline, mas nenhum modelo o supera na maioria dos produtos — em 8 dos 14 produtos (entre eles café, carne bovina, feijão, leite e pão francês), o baseline tem o menor MAE de todos. A @fig-mae ilustra essa comparação para todos os produtos e modelos.

#figure(
  image("../../reports/figures/04_mae_relativo_baseline.png", width: 92%),
  caption: [MAE de cada modelo em relação ao baseline, por produto],
) <fig-mae>

Esse padrão é consistente com uma conclusão negativa válida: com apenas 48 meses de histórico por produto, pode não haver dados suficientes para que um modelo mais complexo aprenda um padrão melhor do que "o preço continua parecido com o de hoje". Random Forest e Gradient Boosting, por serem baseados em árvores, têm ainda uma limitação estrutural adicional — não extrapolam além do maior preço visto no treino. Em 6 dos 14 produtos (feijão, leite, açúcar, banana nanica, carne bovina coxão mole e pão francês), o preço máximo do período de teste supera o máximo visto no treino, o que tende a fazer esses dois modelos subestimar o preço nesses casos por uma limitação estrutural, e não por falta de padrão nos dados.

Quanto ao acerto de direção (sobe/não sobe), os resultados variam por produto sem um padrão tão claro quanto no erro de valor, o que reforça que acertar o valor e acertar a direção são, de fato, informações distintas — um modelo pode errar o valor em poucos centavos e ainda assim acertar (ou errar) a decisão de compra.

== Questão 3 — agrupamento de mercados

A @tab-criterios-k resume os quatro critérios usados para escolher $k$.

#figure(
  caption: [Critérios de escolha do número de grupos ($k$)],
  table(
    columns: 4,
    stroke: none,
    align: (center, right, right, right),
    table.hline(),
    table.header([*k*], [*Inércia*], [*Silhueta*], [*Xie-Beni*]),
    table.hline(stroke: 0.5pt),
    [2], [2,889], [0,370], [0,300],
    [*3*], [1,897], [0,375], [*0,244*],
    [4], [1,510], [*0,377*], [0,256],
    [5], [1,239], [0,361], [0,284],
    [6], [0,943], [0,367], [0,305],
    table.hline(),
  )
) <tab-criterios-k>

O cotovelo e o índice Xie-Beni apontam $k=3$ (maior queda de inércia entre $k=2$ e $k=3$, e mínimo do Xie-Beni); a silhueta em torno de 0,37 fica praticamente empatada entre $k=2$, $3$ e $4$ e não desempata — um valor nessa faixa indica estrutura moderada, isto é, os mercados formam mais um gradiente de preço do que blocos bem separados. A @fig-k ilustra a curva de inércia e os demais critérios.

#figure(
  image("../../reports/figures/05_escolha_k.png", width: 92%),
  caption: [Critérios de escolha de $k$: cotovelo, silhueta e índice Xie-Beni],
) <fig-k>

Com $k=3$, o agrupamento resulta em: um grupo de 10 mercados mais baratos (9% abaixo da mediana geral, mais baratos nos 13 produtos simultaneamente), um grupo de 11 mercados intermediários (6% acima da mediana, mais caros sobretudo em industrializados) e um grupo de 4 mercados mais caros (12% acima da mediana, mais caros sobretudo no hortifrúti — batata 38% e banana nanica 37% acima da mediana). A @fig-perfil detalha o perfil de preço relativo de cada grupo, produto a produto.

#figure(
  image("../../reports/figures/05_perfil_grupos.png", width: 92%),
  caption: [Perfil de preço relativo de cada grupo, por produto],
) <fig-perfil>

A @tab-estabilidade mostra que os grupos se mantêm estáveis ao longo de quatro períodos de 12 meses: o índice Rand ajustado contra o período completo nunca cai abaixo de 0,67, e a correlação de Spearman da ordem dos mercados fica sempre entre 0,96 e 0,99 — ou seja, mesmo quando um mercado muda de grupo, sua posição relativa entre os mais baratos e os mais caros quase não se altera.

#figure(
  caption: [Estabilidade do agrupamento em períodos de 12 meses],
  table(
    columns: 4,
    stroke: none,
    align: (left, right, right, right),
    table.hline(),
    table.header([*Período*], [*ARI vs. completo*], [*% no mesmo grupo*], [*Spearman*]),
    table.hline(stroke: 0.5pt),
    [set/2022 a ago/2023], [0,672], [88%], [0,956],
    [set/2023 a ago/2024], [0,806], [92%], [0,977],
    [set/2024 a ago/2025], [0,897], [96%], [0,987],
    [set/2025 a ago/2026], [0,855], [96%], [0,968],
    table.hline(),
  )
) <tab-estabilidade>

#figure(
  image("../../reports/figures/05_grupos_por_periodo.png", width: 92%),
  caption: [Grupos de mercados em cada período de 12 meses],
) <fig-periodos>

Convertendo a diferença de preço relativo em reais pela Cesta Básica do DIEESE, aos preços médios dos últimos 12 meses da base, a cesta custa em média R\$ 664,53 por mês no grupo mais barato, R\$ 736,01 na mediana entre mercados e R\$ 838,30 no grupo mais caro (@tab-economia e @fig-custo). Isso representa uma economia de R\$ 71,48 por mês (9,7%) ao escolher o grupo mais barato em vez da mediana, e de R\$ 173,77 por mês — cerca de R\$ 2.085 por ano — em relação ao grupo mais caro.

#figure(
  caption: [Custo mensal da cesta básica (DIEESE) por grupo de mercado],
  table(
    columns: 3,
    stroke: none,
    align: (left, center, right),
    table.hline(),
    table.header([*Grupo*], [*Mercados*], [*Custo da cesta/mês*]),
    table.hline(stroke: 0.5pt),
    [Mais baratos], [10], [R\$ 664,53],
    [Intermediários], [11], [R\$ 769,97],
    [Mais caros], [4], [R\$ 838,30],
    [_Mediana entre mercados_], [_—_], [_R\$ 736,01_],
    table.hline(),
  )
) <tab-economia>

#figure(
  image("../../reports/figures/05_custo_cesta_mercados.png", width: 92%),
  caption: [Custo da cesta básica por mercado, ordenado do mais barato ao mais caro],
) <fig-custo>

= Conclusão

A Q1 recebe uma resposta parcialmente negativa, e essa é uma conclusão válida, não uma falha da análise: nenhum dos modelos testados supera o baseline ingênuo de forma consistente entre os 14 produtos. A regressão linear é a abordagem que mais se aproxima, batendo o baseline em 6 produtos, mas em mais da metade dos casos o melhor palpite continua sendo "o preço do mês seguinte é parecido com o de hoje". Isso indica que, com um histórico de apenas 48 meses por produto, os dados atuais não sustentam um modelo de previsão de curto prazo claramente melhor do que a repetição do preço atual — o que, do ponto de vista de quem planeja orçamento, já é uma informação útil: não há, hoje, uma alternativa confiável e simples ao preço mais recente observado.

A Q3 recebe uma resposta afirmativa e quantificada: existem, sim, mercados consistentemente mais baratos. O agrupamento identifica três grupos com perfis de preço distintos, estáveis ao longo de quatro anos de dados, e a diferença entre escolher bem e escolher mal onde comprar é substancial — da ordem de R\$ 2 mil por ano para uma família que segue a Cesta Básica do DIEESE. Esse resultado tem aplicação direta para o consumidor que hoje não sabe, de forma sistemática, onde comprar de forma consistentemente mais barata.

Duas limitações atravessam as duas questões. Primeiro, o tamanho da série: 48 meses é pouco tanto para o aprendizado de padrões de previsão (Q1) quanto para medir estabilidade de grupos em janelas mais curtas (Q3, cuja última janela de 12 meses se apoia em menos meses por mercado). Segundo, a anonimização dos mercados: o trabalho mostra que mercados consistentemente mais baratos existem e quantifica o valor dessa escolha, mas não identifica quais são — uma limitação inerente à base de dados disponível, não ao método. Como trabalho futuro, a mesma abordagem poderia ser revisitada com mais anos de coleta, o que tende a favorecer tanto modelos de previsão mais complexos (Q1) quanto uma estimativa de estabilidade mais robusta dos grupos de mercado (Q3).

#titulo-sem-numero[Referências]
#set par(first-line-indent: 0cm, leading: 0.65em)

#block(above: 1em, below: 1.2em)[
  BRASIL. #emph[Decreto-Lei nº 399, de 30 de abril de 1938]. Aprova a Consolidação das Leis que criam as Comissões de Salário Mínimo e institui a cesta básica de referência. Rio de Janeiro, 1938.
]

#block(above: 0em, below: 1.2em)[
  CONAB — COMPANHIA NACIONAL DE ABASTECIMENTO. #emph[Custos de produção agropecuária]. Brasília: CONAB, 2026. Disponível em: https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao. Acesso em: 24 nov. 2026.
]

#block(above: 0em, below: 1.2em)[
  DIEESE — DEPARTAMENTO INTERSINDICAL DE ESTATÍSTICA E ESTUDOS SOCIOECONÔMICOS. #emph[Metodologia da Pesquisa Nacional da Cesta Básica de Alimentos]. São Paulo: DIEESE, ago. 2025.
]

#block(above: 0em, below: 1.2em)[
  PEDREGOSA, F. et al. Scikit-learn: machine learning in Python. #emph[Journal of Machine Learning Research], v. 12, p. 2825-2830, 2011.
]

#block(above: 0em, below: 1.2em)[
  PUC CAMPINAS. #emph[Enunciado do trabalho final] — disciplina Sistemas Inteligentes e Aprendizado de Máquina. Campinas: PUC Campinas, 2026. Material de disciplina.
]
