# agent-spec.md — modelo do meu agente

<!--
Este arquivo é para preencher, não para ler e devolver. As perguntas de cada
seção estão em comentário como este: elas não aparecem na pré-visualização,
aparecem no editor. Responda ABAIXO de cada seção, apagando nada delas.

As seções que ainda não foram vistas em aula ficam de pé, com a linha
"quando se preenche" dizendo o encontro em que isso acontece. O documento
cresce a cada laboratório — o de hoje é o primeiro.

Preencha com exemplos concretos do SEU domínio. Uma linha que funcionaria
para qualquer empresa é uma linha genérica — o exemplo do seu segmento
(agente-spec-exemplo.pdf, no mesmo pacote) mostra o contraste.
-->

**Domínio:** AMS · Assistente de Manutenção Segura (risco de falha, normas e bloqueio em ordens de serviço industriais)
**Autor(a):** Leodocir · **Última revisão:** 15/10/2026

---

## 1. PEAS

<!-- Perguntas que guiam o preenchimento:
  - Performance: o que conta como sucesso, em uma fórmula? Sobre o quê se
    conta, sobre qual conjunto, quanto é sucesso? Qual termo impede a
    trapaça mais óbvia (fechar rápido sem resolver)?
  - Environment: onde o agente opera? O que existe lá — sistemas, pessoas,
    documentos, ruído? Cite elementos concretos.
  - Actuators: o que o agente pode FAZER? Inclua comunicar e escalar:
    informar a decisão é uma ação, e passar adiante também é.
  - Sensors: o que o agente consegue PERCEBER? Só o que ele enxerga existe
    para ele.
  Um PEAS que menciona tecnologia de solução (banco vetorial, nome de modelo)
  está descrevendo a solução — o PEAS descreve o problema.
-->
**Quando se preenche:** no Laboratório 01, hoje. Refinado na Atividade Orientada.

**Performance:**

**Fórmula (primária): taxa de captura de falha, com teto de alarme falso.**

- **Sobre o quê se conta:** das ordens de serviço cuja leitura de sensores
  terminou em falha (`Machine failure = 1`), a fração que o agente classificou
  com risco **médio ou alto**.
  `captura = ordens com falha classificadas médio/alto ÷ total de ordens com falha`
- **Sobre qual conjunto:** uma partição de teste fixa de 2.000 registros do
  AI4I 2020 (amostra estratificada pela falha, semente fixa, ~68 falhas),
  separada antes de qualquer ajuste.
- **Quanto é sucesso:** captura **≥ 80%**. **Hoje:** o baseline "nunca falha"
  captura 0% (com 96,6% de acurácia, o que mostra que acurácia não serve de
  medida aqui). A melhor regra de um limiar só (desgaste > 245 min) captura
  4 das 339 falhas do dataset, ou 1,2%.
- **Termo contra a trapaça:** classificar tudo como "alto" daria captura de
  100%. Por isso a medida só vale se o **alarme falso** (ordens *sem* falha
  classificadas médio/alto ÷ total de ordens sem falha) ficar **≤ 15%**.
  Acima disso, a meta conta como não atingida, porque parar máquina à toa
  tem custo de produção e faz o técnico ignorar o parecer.
- **Termo de segurança:** **zero** ordens com intervenção em máquina
  energizada sem a recomendação de bloqueio (LOTO), num conjunto de 30
  ordens rotuladas pelo supervisor de segurança. Hoje: ainda não medido. O
  dataset não traz esse rótulo, e montar o conjunto é trabalho da D7.

**Environment:**

- A **planta de usinagem**: máquinas de três tipos de produto (L, M e H,
  60/30/10% do parque), cada uma com sensores de temperatura do ar e do
  processo, rotação, torque e desgaste da ferramenta.
- O **sistema de ordens de serviço**, onde chega a ordem com identificador,
  máquina e uma **descrição em texto livre** escrita às pressas ("troca do
  insert de corte do eixo 3 e regulagem da folga").
- As **pessoas**: o **técnico de manutenção**, que executa a ordem e tem a
  decisão final, com pouco tempo entre uma ordem e outra; e o **supervisor de
  segurança**, que audita as recomendações depois.
- Os **documentos**: NR-10 (instalações elétricas), NR-12 (máquinas e
  equipamentos) e NR-35 (trabalho em altura).
- O **ruído**: falhas raras (3,4% dos registros) e multicausais (cinco modos:
  TWF, HDF, PWF, OSF e RNF); falhas aleatórias sem causa nos sensores (RNF);
  27 registros com falha marcada e nenhum modo; descrições incompletas, que
  não dizem se há painel elétrico ou altura no local.

**Actuators:**

- **Classificar o risco de falha** da máquina: baixo, médio ou alto.
- **Indicar as normas aplicáveis** à intervenção (NR-10, NR-12, NR-35).
- **Recomendar ou não o bloqueio e etiquetagem (LOTO)** antes de começar.
- **Comunicar o parecer ao técnico**: resposta curta e justificada (o que
  pesou na decisão), registrada para auditoria.
- **Escalar ao supervisor de segurança**: quando o risco é alto, quando os
  dados são inconsistentes (falha marcada sem modo, leitura fora da faixa
  física) ou quando a descrição não permite decidir as normas.
- **Pedir informação ao técnico**: perguntar o que a descrição não diz
  ("há painel elétrico no ponto de intervenção?", "o trabalho é acima de 2 m?").

**Sensors:**

- A **leitura atual dos sensores** da máquina: temperatura do ar e do
  processo (K), rotação (rpm), torque (Nm) e desgaste da ferramenta (min).
- O **tipo de produto** em usinagem (L/M/H) e o identificador da máquina.
- O **texto da descrição** da ordem de serviço. É o único canal pelo qual o
  agente fica sabendo *o que* vai ser feito e *onde*.
- O **texto das normas** NR-10, NR-12 e NR-35.

O que não está nesses canais não existe para o agente: o **histórico de
intervenções** da máquina, a **condição da equipe** (treinamento, cansaço,
EPI disponível) e o **ambiente físico** do ponto de intervenção. Esses só
chegam se alguém os escrever na descrição. E a **causa** da falha nunca é
observada direto: só se enxergam os sintomas nos sensores.

---

## 2. O ambiente em sete dimensões

<!--
Perguntas que guiam o preenchimento (uma por dimensão):
  - Observabilidade: existe algo que muda a decisão e o agente não mede?
  - Número de agentes: existe alguém cujas ações mudam o seu resultado?
    Um humano que reage ao agente conta.
  - Determinismo: a mesma ação no mesmo estado dá sempre o mesmo efeito?
  - Episódico ou sequencial: a decisão de agora afeta as decisões seguintes?
  - Estático ou dinâmico: o ambiente muda enquanto o agente delibera?
  - Discreto ou contínuo: estados e ações são contáveis?
  - Conhecido ou desconhecido: o agente sabe de antemão as regras? (Trata do
    que ele SABE, não do que ele VÊ.)
  Cada classificação vem com uma frase de justificativa — a etiqueta sozinha
  não vale nada.
-->
**Quando se preenche:** no Laboratório 02, no sábado (encontro 2).

| Dimensão | Classificação | Justificativa | O que obriga no projeto |
|---|---|---|---|
| Observabilidade | **Parcialmente observável** | O histórico da máquina, a condição da equipe e o que há no local (painel elétrico, altura) mudam a decisão correta, e o agente não mede nada disso; só sabe o que vier escrito na descrição. | Estado interno, memória e contexto; a ação "pedir informação ao técnico" existe por causa disso. Elimina o agente reativo simples. |
| Número de agentes | **Agente único** (depende) | O técnico e o supervisor agem *depois* do parecer e não disputam a decisão. Cada ordem é avaliada sem ver como o técnico reagiu à anterior. Se a rejeição do técnico passar a realimentar o agente, ele vira multiagente. | Hoje, nenhum protocolo de comunicação nem previsão do outro. Fica registrado o gatilho que mudaria isso. |
| Determinismo | **Estocástico** | A mesma leitura pode terminar ou não em falha: o próprio dataset tem falhas aleatórias (RNF, 19 casos) sem causa nos sensores, e o parecer passa por um modelo de linguagem, que não responde igual duas vezes. | Valor esperado (decidir por probabilidade × custo do erro), nova tentativa com tempo máximo na chamada do modelo e validação da saída. |
| Episódico ou sequencial | **Episódico** | Cada ordem de serviço é avaliada sozinha: errar o parecer de uma não muda a leitura nem a decisão da seguinte. | Não precisa de planejamento nem de avaliação de trajetória: a avaliação é por conjunto de casos independentes (a partição de teste). |
| Estático ou dinâmico | **Semidinâmico** | A máquina está parada para a ordem e a leitura não muda enquanto o agente decide, mas o técnico tem pouco tempo entre ordens: parecer atrasado perde valor. | Prazo de resposta, e uma resposta parcial aceitável (por exemplo, recomendar LOTO por precaução se o modelo não responder a tempo). |
| Discreto ou contínuo | **Contínuo** na percepção, **discreto** na decisão | Temperatura, rotação, torque e desgaste variam sem degraus; a saída (3 níveis de risco, 3 normas, LOTO sim/não) é contável. | Discretização declarada, com granularidade justificada: os limiares de cada modo (HDF com ΔT < 8,6 K e rotação < 1380 rpm; OSF por desgaste × torque, conforme o tipo; TWF entre 200 e 240 min de desgaste). Três níveis e não cinco, porque o técnico precisa decidir rápido. |
| Conhecido ou desconhecido | **Conhecido** | As regras estão documentadas: a física dos modos de falha vem publicada com o dataset, e as NRs são texto oficial. O agente não precisa experimentar para descobrir o que cada ação provoca. | Sem fase de exploração. A ressalva vale para uma planta real, onde o comportamento de cada máquina teria de ser aprendido do histórico. |

**Dimensão mais difícil (apresentação de 2 minutos):** número de agentes. A
justificativa completa está no `D2/RESUMO-DEFESA-D2.md`.

---

## 3. Tipo de agente pretendido

<!--
Perguntas que guiam o preenchimento:
  - O tipo mais simples que resolve: reativo simples, baseado em modelo,
    baseado em objetivos, baseado em utilidade, ou um deles com aprendizagem?
  - A caracterização do ambiente (seção 2) é que decide — parcialmente
    observável elimina o reativo simples.
  - Justifique com a dimensão do ambiente que obriga a escolha.
-->
**Quando se preenche:** no sábado (encontro 2, manhã).

[o tipo mais simples que resolve, justificado pela dimensão
do ambiente que o obriga]

---

## 4. Medida de desempenho

<!--
Perguntas que guiam o preenchimento:
  - A fórmula do campo Performance, agora em definição operacional: como se
    calcula, passo a passo, sem ambiguidade?
  - Métrica primária e duas secundárias. As secundárias pegam o que a
    primária deixa passar (custo, latência, reabertura).
  - O conjunto de casos: de onde vêm, quantos são, de que período.
  - O limiar de sucesso e o valor de hoje.
-->
**Quando se preenche:** a fórmula começa no Laboratório 01; a definição
operacional completa — primária, secundárias, conjunto e limiar — é item da
Atividade Orientada.

[métrica primária e duas secundárias, cada uma com: como se
calcula, sobre qual conjunto, qual o limiar de sucesso e o
valor de hoje]

---

## 5. Restrições

<!--
Perguntas que guiam o preenchimento:
  - Latência aceitável: a partir de quantos segundos a resposta perde valor?
  - Custo aceitável: quanto pode custar cada resolução?
  - O que o agente jamais pode fazer: a ação irreversível que ele não executa
    sozinho. Esta linha vira política em D12.
  - A troca que você aceita: quanto de qualidade por quanto de custo?
    Um exemplo numérico vale mais que a fórmula.
-->
**Quando se preenche:** na Atividade Orientada.

[latência aceitável, custo aceitável, o que o agente jamais
pode fazer sozinho, e a troca qualidade × custo que você
aceita — com um exemplo numérico]

---

## 6. Catálogo de ações

<!--
Perguntas que guiam o preenchimento:
  - Para cada ação: nome, entrada, saída, é reversível?, qual o risco se
    errar? As quatro colunas são obrigatórias — "baixo" não é descrição de
    risco.
  - Ações de leitura E de escrita: as que alteram o mundo são as que exigem
    cuidado, e são justamente as que mais ficam de fora.
  - Este catálogo é, literalmente, a lista de ferramentas que você vai
    implementar em D10.
-->
**Quando se preenche:** na Atividade Orientada — o pacote `D2-07` traz o
modelo da tabela e dois exemplos preenchidos.

[tabela: nome · entrada · saída · é reversível? · risco se
errar — ações de leitura e de escrita]

---

## 7. Formulação por busca

<!--
Perguntas que guiam o preenchimento:
  - Qual fatia do problema é um espaço de estados? (Nem toda fatia é — e
    reconhecer a que não é vale tanto quanto formular a que é.)
  - Os cinco componentes: estado inicial, ações, modelo de transição, teste
    de objetivo, custo de caminho. Comece pelo teste de objetivo.
  - O estado descreve a SITUAÇÃO, não a história de como se chegou nela.
-->
**Quando se preenche:** no Laboratório 03, sábado à tarde (encontro 2).

**A fatia que é busca:** em que ordem o técnico confere os itens de segurança
de uma ordem de serviço e fecha as pendências que eles abrem. É o
**subproblema 3 do catálogo (roteiro de conformidade)** com os dados do AMS
(caminho padrão). O código está em `D2/D2-03-formular-como-busca/meu_problema.py`.

Caso formulado: OS-2026-0001, máquina M14860 (tipo M), "troca do insert de
corte do eixo 3 e regulagem da folga". Roteiro de 7 itens (sensores, fontes
de energia/NR-12, painel elétrico/NR-10, proteções e intertravamentos/NR-12,
altura/NR-35, EPI, ferramenta de reposição). Quatro deles abrem pendência:
LOTO, desenergizar e testar a ausência de tensão, proteção provisória e luva
anticorte.

| Componente | Neste domínio |
|---|---|
| Estado inicial | Nenhum item conferido e nenhuma pendência aberta: `((), ())` |
| Ações | `verificar:<item>` para cada item ainda não conferido; `resolver:<pendência>` para cada pendência aberta |
| Transição | Verificar soma o item aos conferidos e abre as pendências que ele revela (ex.: conferir o painel elétrico abre "desenergizar e testar a ausência de tensão"). Resolver tira a pendência das abertas |
| Teste de objetivo | Todos os itens do roteiro conferidos **e** nenhuma pendência aberta: a intervenção está liberada |
| Custo | Minutos do técnico. Conferir um item com pendência aberta custa o **dobro** (conferir com a máquina ainda energizada ou sem proteção obriga a reconferir depois) |

O estado é o par **(itens conferidos, pendências abertas)**, cada um como tupla
ordenada. Guarda a *situação*, não a ordem em que as coisas foram feitas:
duas trilhas que chegam aos mesmos itens e pendências são o mesmo estado.

**Teste de sanidade:** `python verificar-formulacao.py meu_problema.py:MEU_PROBLEMA`
passou nas seis verificações (6 ✅ · 0 ⚠️ · 0 ❌). O espaço tem 648 estados.

**O que não é busca neste domínio:** classificar o risco é **classificação**
sobre os sensores (o modelo que a D5 tenta fazer bater a regra do desgaste);
escolher as normas é **regra mais recuperação de texto** (D9); recomendar o
LOTO é **regra** (intervenção com energia presente → bloqueio). A fatia de
busca vale porque é a parte em que a ordem muda o custo total. Fechar uma
pendência antes de seguir evita retrabalho.

**Limitação declarada:** a formulação não impõe precedência. Ela aceita
conferir as proteções antes do bloqueio, porque conferir é inspeção e não
intervenção. Se a política da planta exigir LOTO antes de qualquer conferência
física, isso vira restrição na função `acoes` (ou custo infinito), e é o
primeiro ajuste a fazer no lab-04.
