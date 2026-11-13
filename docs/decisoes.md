# Decisões do projeto

Este arquivo registra **o que** foi decidido e **por quê**, para que qualquer integrante do grupo entenda as escolhas antes de mexer no código. Se uma decisão mudar, atualize aqui com a data e o motivo; não apague a anterior, risque ou marque como substituída.

Última revisão: 13/11/2026

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
- **Ensemble** (aula 10): média ou stacking dos modelos acima.

**Q1 — modelo extra: a decidir após os primeiros resultados.** Candidato principal: **Random Forest** (bagging de árvores; bagging é citado na aula 10).
- O enunciado incentiva "estudar e aprender outros modelos", mas um modelo extra **não é necessário** para responder a questão.
- Ele faz sentido se os modelos da aula não forem suficientes. Por exemplo, a regressão linear só capta relações em linha reta, e a relação entre custo do produtor e preço pode não ser linear.
- Regra: rodar primeiro os modelos da aula. Se já baterem o baseline com folga, o extra entra só como comparação ("testamos um modelo mais complexo e ele não melhorou", que também é conclusão). Se nenhum bater o baseline, o extra ajuda a descobrir se o problema é o modelo simples demais ou se os dados realmente não permitem prever. Princípio: **adicionar complexidade só quando os dados mostrarem necessidade.**

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
