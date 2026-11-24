# Como funciona a previsão de preços (Q1)

Este texto explica, de forma geral e sem entrar em código, como a parte de
previsão de preços do trabalho funciona. A ideia é que qualquer pessoa do
grupo — ou alguém de fora, lendo o relatório — entenda o raciocínio sem
precisar olhar uma linha de programação.

## A pergunta

Todo mês, os produtos da cesta básica (café, arroz, feijão, leite, entre
outros) têm um preço que sobe e desce. A pergunta que essa parte do trabalho
responde é simples de enunciar e difícil de responder bem: **dado o
histórico de preços de um produto, é possível adivinhar quanto ele vai custar
no mês seguinte melhor do que simplesmente apostar que o preço não muda?**

Essa segunda parte — "melhor do que apostar que não muda" — é importante.
Não basta construir algo que dê um número; esse número precisa ser mais útil
do que o palpite mais simples possível, que é dizer "vai custar a mesma
coisa que custa hoje". Esse palpite simples é o ponto de partida de toda a
análise: qualquer método mais sofisticado só vale a pena se bater essa régua.

## De onde vem o preço usado

A base original tem uma coleta de preço por produto, por mercado, por dia —
dezenas de mercados, coletando os mesmos produtos em dias diferentes do mês.
Usar esse dado "bruto" para prever o futuro seria complicado: cada mercado
tem suas próprias promoções, erros de digitação e particularidades, e isso
criaria uma série cheia de ruído.

Por isso, antes de qualquer previsão, os preços de todos os mercados em um
mesmo mês são resumidos em um único número por produto: o preço "típico"
daquele mês, calculado de uma forma que não se deixa enganar por valores
muito fora da curva (uma promoção agressiva ou um preço digitado errado não
distorcem esse número tanto quanto distorceriam uma média simples). O
resultado é uma série de aproximadamente quatro anos, com um preço por mês
para cada um dos catorze produtos analisados.

## Como se ensina o modelo a olhar para o passado

A intuição central é bem humana: se eu quero adivinhar quanto vai custar o
café no mês que vem, uma informação óbvia é "quanto custa agora" — e outra
informação útil é "como ele andou subindo ou caindo nos últimos meses".

Então, para cada mês da série, o modelo recebe como pista o preço daquele
mês e de alguns meses anteriores, e é treinado para responder "qual vai ser
o preço do mês seguinte?". Repetindo isso para cada mês da história, o
modelo acumula muitos exemplos de "esse foi o histórico recente, e esse foi
o preço que realmente veio depois" — e aprende, com isso, um padrão que
tenta generalizar para o mês seguinte ao fim da série, que é o que realmente
importa prever.

Quantos meses de histórico mostrar ao modelo não é uma escolha óbvia: mostrar
pouco histórico pode fazer o modelo perder uma tendência mais longa; mostrar
demais, com uma série de poucos anos, pode fazer sobrar pouco exemplo de
treino. Esse ajuste é decidido testando algumas opções e verificando qual
funciona melhor, da forma explicada a seguir.

## Por que não se pode mostrar o futuro durante o treino

Esse é talvez o cuidado mais importante de toda essa parte do trabalho.
Como a série é temporal — isto é, a ordem no tempo importa — não se pode
simplesmente misturar todos os meses, treinar com uma mistura aleatória
deles e testar com outra mistura aleatória. Se isso fosse feito, o modelo
poderia, sem querer, aprender com um mês mais recente para "prever" um mês
mais antigo — o que é um tipo de trapaça: na vida real, ninguém tem acesso
ao futuro quando precisa decidir o preço do mês que vem.

Por isso, a avaliação é sempre feita respeitando a ordem do tempo: o modelo
só vê os meses mais antigos durante o treino, e é testado nos meses que vêm
depois, nunca o contrário. Para deixar esse teste mais robusto — já que a
série inteira tem só uns quatro anos, e testar em um único período poderia
ser sorte ou má sorte — o processo é repetido mês a mês: treina com tudo até
um certo mês, testa no mês seguinte, depois avança um mês e repete, dezenas
de vezes. Isso dá um retrato mais confiável do desempenho do que testar numa
única janela de meses.

## Como se ajustam os detalhes do modelo sem "colar a resposta"

Alguns modelos têm ajustes internos — por exemplo, quantos meses de
histórico olhar, ou quantos "casos parecidos do passado" considerar na hora
de comparar. Esses ajustes não podem ser escolhidos olhando para o
resultado no teste final, porque isso seria, de novo, uma forma de colar a
resposta: eu estaria escolhendo o ajuste que dá certo justamente no período
que deveria servir para avaliar honestamente o modelo.

A solução é reservar uma fatia extra, só para ajuste, que fica dentro do
próprio período de treino e nunca toca no período de teste final. Vários
ajustes candidatos são testados nessa fatia reservada, e só o que tiver o
menor erro ali é usado depois no teste de verdade. Assim, quando o modelo
finalmente é avaliado no período de teste, ele está usando ajustes
decididos sem nunca ter visto esse período.

## Os "candidatos" testados

Cinco abordagens diferentes são comparadas lado a lado para cada produto:

- **O palpite simples**, que serve de régua: supõe que o preço do mês
  seguinte vai ser igual ao de hoje. Qualquer abordagem mais elaborada
  precisa superar isso para ser considerada útil.
- **Uma linha de tendência**, que procura uma relação direta entre o
  histórico recente e o preço seguinte — funciona bem quando o preço sobe ou
  cai de forma razoavelmente constante, e tem dificuldade quando o
  comportamento é mais irregular.
- **Uma comparação com situações parecidas**, que olha para outros momentos
  do passado com um histórico de preços semelhante ao do momento atual, e
  usa o que aconteceu depois naqueles momentos como palpite para agora.
- **Uma combinação das três abordagens acima**, por média ponderada (quem
  errou menos na validação pesa mais).
- **Um conjunto de árvores de decisão** (Random Forest), capaz de captar
  relações que não sejam uma linha reta — por exemplo, entre o custo do
  produtor e o preço final. É a abordagem "extra", opcional, incluída só
  depois de ver que nenhuma das anteriores bate o palpite simples com folga;
  serve para checar se o problema é essas abordagens serem simples demais ou
  se o preço desses produtos realmente é difícil de prever com o histórico
  disponível. Uma variante dela (Gradient Boosting) também foi testada só
  para comparação, sem fazer parte da avaliação oficial.

Além do histórico de preços, para quatro dos catorze produtos — os que têm
uma ligação mais direta com a agricultura (grãos e leite) — também foi
testada como pista adicional uma estimativa de quanto custa para o produtor
fabricar aquele item. A ideia por trás disso é que um aumento no custo de
produção tende a chegar, com algum atraso, no preço final de mercado. Como
essa fonte traz só um valor por ano e a comparação com e sem ela não mostrou
ganho consistente sobre o palpite simples, essa pista **não entra nos modelos
finais**. O teste e a justificativa estão no notebook 03 e na decisão 5.

## Como se mede se valeu a pena

O resultado de cada modelo é medido de duas formas, porque elas respondem
perguntas diferentes:

A primeira é **o tamanho do erro em reais**: em média, quanto a previsão
erra em relação ao preço real do mês seguinte? Essa resposta importa para
quem planeja orçamento com antecedência — uma ONG, um banco de alimentos,
uma família — e quer saber quanto dinheiro reservar.

A segunda é **se a direção foi acertada**: independente do valor exato, o
modelo acertou se o preço ia subir ou não subir? Essa resposta importa para
quem decide o momento de comprar — vale a pena comprar agora, antes de uma
alta, ou dá para esperar? Um modelo pode errar o valor exato por poucos
centavos e ainda assim acertar a decisão mais importante, que é se o preço
vai subir ou não; por isso essas duas medidas são sempre reportadas
separadamente, nunca misturadas em um único número.

É importante dizer também que uma conclusão negativa — nenhum modelo
conseguindo superar o palpite simples — não é um fracasso da análise. Com
poucos anos de histórico, é perfeitamente possível que o preço de alguns
produtos seja difícil de prever no curto prazo, e essa descoberta também é
um resultado útil: significa que, para esses produtos, a melhor estimativa
disponível realmente é "o preço continua parecido com o de hoje".

## Onde isso está agora

No momento, o palpite simples, a linha de tendência, a comparação com
situações parecidas e a combinação das três (ensemble) já estão funcionando
e sendo avaliados para todos os catorze produtos, com a série de preços real
(não mais fictícia), junto com a escolha automática dos ajustes internos de
cada um. A pista extra do custo do produtor já foi testada e ficou fora
dos modelos finais (decisão 5, notebook 03). Todos os produtos são testados
nos mesmos 11 meses (decisão 7, atualização), e cada modelo escolhe seu
próprio número de meses de histórico em vez de reaproveitar o que foi
escolhido para a comparação com situações parecidas (decisão 6, atualização).

A combinação foi feita por **média ponderada** (peso de cada modelo = 1 /
erro de validação, calculado sem olhar o teste), e não por stacking: com
pouco mais de dois anos de treino por produto, um modelo que aprendesse a
combinar os outros teria poucos exemplos para aprender algo confiável. O
ensemble bate o palpite simples em **4 dos 14 produtos** (Banana Nanica,
Batata, Manteiga, Óleo) — nos outros, mesmo dando mais peso ao modelo mais
confiável na validação, misturar com os modelos mais fracos piorou o erro em
relação ao palpite simples sozinho. Isso é consistente com o ponto abaixo:
quando o palpite simples já é difícil de bater, qualquer combinação que
inclua os modelos mais fracos tende a herdar parte do erro deles.

A **linha de tendência** (regressão linear) é a que mais se aproxima do
palpite simples: bate em **6 dos 14 produtos** (Arroz, Banana Nanica,
Batata, Farinha de Trigo, Manteiga, Tomate) — melhor taxa entre todas as
abordagens testadas, desde que passou a escolher seu próprio número de
meses de histórico em vez do que foi escolhido para a comparação com
situações parecidas.

Com o ensemble também não batendo o palpite simples na maioria dos
produtos, o modelo extra (decisão 6) foi decidido: **Random Forest**, com
`max_depth` e `min_samples_leaf` pequenos para não decorar o treino (só
~30 meses por produto). Resultado: a Random Forest bate o palpite simples em
**5 dos 14 produtos** (Arroz, Açúcar, Banana Nanica, Manteiga, Óleo) — taxa
parecida com a do ensemble, não uma melhora clara sobre a linha de
tendência. Isso aponta mais para "o preço desses produtos é difícil de
prever com este histórico" do que para "os modelos mais simples eram fracos
demais".

Testamos também Gradient Boosting só por comparação (não é modelo oficial
da decisão 6): ele ficou pior que a Random Forest em 9 dos 14 produtos, só
superando em 5 (Açúcar, Batata, Leite, Manteiga, Óleo). Com poucos meses de
treino por produto, o ajuste mais fino do boosting (taxa de aprendizado,
várias árvores em sequência) não parece compensar — reforça que o fator
limitante aqui é a quantidade de dados, não o tipo de modelo.

Uma limitação conhecida de ambos, por serem baseados em árvores: eles não
extrapolam além do maior preço visto no treino. Em produtos com tendência de
alta (Feijão, Leite, Açúcar, Banana Nanica, Carne Bovina Coxão Mole, Pão
Francês — ver tabela de diagnóstico no notebook 04), isso tende a
subestimar o preço do teste por esse motivo estrutural, não por falta de
padrão nos dados.

Com a série real, o palpite simples (baseline) bate as outras abordagens em
erro de valor (MAE) na maioria dos catorze produtos — sinal de que, com
apenas 48 meses de histórico, pode não haver dados suficientes para um
modelo mais complexo aprender um padrão melhor do que "o preço continua
parecido com o de hoje". Essa é uma conclusão negativa válida (ver seção
"Como se mede se valeu a pena") e deve ser reportada como tal no relatório,
em vez de escondida. Tabelas completas em `reports/tables/04_q1_resultados.csv`
e `04_q1_extrapolacao.csv`; figura comparando o erro de cada modelo com o do
palpite simples em `reports/figures/04_mae_relativo_baseline.png`.
