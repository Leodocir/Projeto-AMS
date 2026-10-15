# Sete dimensões — perguntas para o meu ambiente

<!--
Este arquivo é o formulário do Laboratório 02: preencha DENTRO dele, na
seção do seu domínio, no fim. As perguntas por dimensão estão em comentário
como este — aparecem no editor, não na pré-visualização.

Em cada dimensão, a resposta tem duas partes obrigatórias: a classificação
e UMA FRASE de justificativa. A justificativa é o que a rubrica pontua — a
etiqueta sozinha não vale nada (slide 32). Quando a resposta honesta for
"depende", escreva de que depende e em que situação cada resposta se
aplica: isso é caracterização melhor, não pior.

Copie a tabela preenchida para a seção 2 do seu agent-spec.md ao terminar.
-->

## As sete perguntas (as mesmas do slide 22)

| Dimensão | A pergunta que ela faz |
|---|---|
| Observabilidade | O agente enxerga tudo o que precisa para decidir? |
| Número de agentes | Existe outro agente cujas ações afetam o resultado? |
| Determinismo | A mesma ação no mesmo estado dá sempre o mesmo efeito? |
| Episódico ou sequencial | A decisão de agora afeta as decisões seguintes? |
| Estático ou dinâmico | O ambiente muda enquanto o agente delibera? |
| Discreto ou contínuo | Estados e ações são contáveis ou variam sem degraus? |
| Conhecido ou desconhecido | O agente sabe de antemão as regras do ambiente? |

## O que prestar atenção em cada uma

- **Observabilidade** — o teste que decide: existe algo que muda a decisão
  correta e que o agente não mede? Se existe, é parcialmente observável,
  e o projeto precisa de estado interno. Quase todo domínio real é
  parcialmente observável; a resposta honesta aqui costuma ser "parcial".
- **Número de agentes** — um humano operador conta, se ele reage ao que o
  agente faz. Se a sua resposta for multiagente, a D11 será central para
  o seu projeto, e não periférica.
- **Determinismo** — é sobre o efeito das ações, não sobre a observação.
  E atenção: qualquer sistema que chame um modelo de linguagem tem uma
  ação estocástica no meio.
- **Episódico ou sequencial** — classificar um lote é episódico; conduzir
  um atendimento é sequencial. A consequência prática é o custo de
  avaliação: episódico avalia casos independentes, sequencial exige
  avaliar trajetórias inteiras.
- **Estático ou dinâmico** — dinâmico impõe prazo: resposta tardia é
  resposta errada. O caso do meio tem nome: semidinâmico, quando o
  ambiente não muda mas a nota do agente cai com a espera.
- **Discreto ou contínuo** — busca funciona sobre enumeração; contínuo
  precisa ser discretizado antes, e toda discretização perde informação.
  Se você discretizar, a granularidade é decisão declarada, com custo dos
  dois lados.
- **Conhecido ou desconhecido** — a distinção que mais confunde: trata do
  que o agente SABE sobre as regras, e não do que ele VÊ. Sistema legado
  sem documentação é ambiente desconhecido, mesmo que se enxergue tudo
  nele.

## As respostas do meu domínio

**Domínio:** AMS · Assistente de Manutenção Segura

| Dimensão | Minha classificação | Justificativa (uma frase) |
|---|---|---|
| Observabilidade | **Parcialmente observável** | O histórico da máquina, a condição da equipe e o que há no local (painel elétrico, altura) mudam a decisão correta, e o agente não mede nada disso; só sabe o que vier escrito na descrição. |
| Número de agentes | **Agente único** (depende) | O técnico e o supervisor agem *depois* do parecer e não disputam a decisão. Cada ordem é avaliada sem ver como o técnico reagiu à anterior. Se a rejeição do técnico passar a realimentar o agente, ele vira multiagente. |
| Determinismo | **Estocástico** | A mesma leitura pode terminar ou não em falha: o próprio dataset tem falhas aleatórias (RNF, 19 casos) sem causa nos sensores, e o parecer passa por um modelo de linguagem, que não responde igual duas vezes. |
| Episódico ou sequencial | **Episódico** | Cada ordem de serviço é avaliada sozinha: errar o parecer de uma não muda a leitura nem a decisão da seguinte. |
| Estático ou dinâmico | **Semidinâmico** | A máquina está parada para a ordem e a leitura não muda enquanto o agente decide, mas o técnico tem pouco tempo entre ordens: parecer atrasado perde valor. |
| Discreto ou contínuo | **Contínuo** na percepção, **discreto** na decisão | Temperatura, rotação, torque e desgaste variam sem degraus; a saída (3 níveis de risco, 3 normas, LOTO sim/não) é contável. |
| Conhecido ou desconhecido | **Conhecido** | As regras estão documentadas: a física dos modos de falha vem publicada com o dataset, e as NRs são texto oficial. O agente não precisa experimentar para descobrir o que cada ação provoca. |

**O que a tabela de consequências obriga no meu projeto** (conferir no
`tabela-de-consequencias.pdf` e colar aqui as linhas que se aplicam):

O que **se aplica** (vira exigência):
- *Parcialmente observável* → **estado interno; memória e contexto.** O agente
  precisa guardar o que o técnico respondeu e pedir o que falta. Elimina o
  reativo simples.
- *Estocástico* → **valor esperado, nova tentativa, tempo máximo.** Decidir o
  risco comparando probabilidade com o custo de cada erro; a chamada do
  modelo já tem novas tentativas e modo sem rede (`ams.llm`).
- *Semidinâmico* (o lado brando do dinâmico) → **prazo de resposta e resposta
  parcial aceitável.** Sem resposta a tempo, recomendar LOTO por precaução e
  escalar.
- *Contínuo* (na percepção) → **discretização declarada, com granularidade
  justificada.** Três níveis de risco, com os limiares físicos de cada modo
  de falha.

O que **não se aplica** (e o projeto economiza):
- *Agente único* → sem protocolo de comunicação nem previsão do outro, com o
  gatilho registrado: se a rejeição do técnico realimentar o agente, isso muda.
- *Episódico* → sem planejamento de trajetória; a avaliação é um conjunto de
  ordens independentes (a partição de teste de 2.000 registros).
- *Conhecido* → sem fase de exploração; as regras vêm das NRs e da física
  documentada do dataset.
