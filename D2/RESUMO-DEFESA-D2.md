# Resumo para a defesa — D2, labs 01 a 03 (AMS)

Uma frase para abrir: **o AMS recebe uma ordem de serviço (leitura dos sensores
mais descrição em texto) e devolve risco de falha, normas aplicáveis e se
precisa de bloqueio (LOTO). A decisão final é do técnico.**

---

## Lab 01 — PEAS (agent-spec.md, seção 1)

**O ponto central é a fórmula de Performance.** Saiba explicar as três perguntas:

| Pergunta | Resposta do AMS |
|---|---|
| Sobre o quê se conta? | Ordens com falha que o agente classificou médio/alto ÷ total de ordens com falha (captura, ou *recall*) |
| Sobre qual conjunto? | Partição de teste fixa de 2.000 registros do AI4I 2020, estratificada (~68 falhas) |
| Quanto é sucesso? | ≥ 80%. **Hoje:** "nunca falha" = 0%; melhor regra de um limiar (desgaste > 245 min) = 1,2% |

**Perguntas que podem vir, e a resposta:**

- *"Por que não usar acurácia?"* A falha é rara (3,4%). Dizer "nunca falha"
  já dá 96,6% de acurácia e não pega nenhuma falha. O notebook (pergunta 7)
  mostrou isso.
- *"E se o agente disser 'alto' para tudo?"* Esse é o termo contra a trapaça:
  o alarme falso tem teto de 15%. Parar máquina à toa custa produção e faz o
  técnico parar de confiar no parecer.
- *"Por que 80% e 15%?"* São metas discutíveis, e é isso que se quer: um
  número dá para discutir, uma intenção não. A ideia é que deixar passar uma
  falha custa mais que um alarme falso, por isso a meta de captura é alta e
  a de alarme é tolerante.
- *"E o LOTO, como se mede?"* Zero omissões de LOTO num conjunto de 30 ordens
  rotuladas pelo supervisor. **Admita:** hoje não está medido, porque o
  dataset não tem esse rótulo e esse conjunto é trabalho da D7.

**Actuators:** lembre que **comunicar** (parecer ao técnico), **escalar**
(supervisor) e **pedir informação** também são ações. É o que a turma mais
esquece.

**Sensors, o limite:** o agente **não vê** o histórico da máquina, a condição
da equipe nem o local físico (se há painel elétrico ou altura). Só sabe o que
vier escrito na descrição. Esse limite é o que justifica a observabilidade
parcial no lab 02.

---

## Lab 02 — Sete dimensões (seção 2)

| Dimensão | AMS | Argumento em uma linha |
|---|---|---|
| Observabilidade | Parcial | Histórico, equipe e local mudam a decisão e não são medidos |
| Nº de agentes | Único (depende) | Técnico e supervisor agem depois e não disputam a decisão |
| Determinismo | Estocástico | Falhas aleatórias (RNF) sem causa nos sensores, e o LLM no meio |
| Episódico/sequencial | Episódico | Uma ordem não muda a seguinte |
| Estático/dinâmico | Semidinâmico | A máquina não muda, mas o técnico tem pressa |
| Discreto/contínuo | Contínuo na percepção, discreto na decisão | Sensores sem degraus; saída em 3 níveis |
| Conhecido/desconhecido | Conhecido | Física e NRs documentadas; não precisa experimentar |

**Consequências que você precisa saber dizer** (é o que dá nota):

- Parcial → memória e contexto, e a ação "pedir informação". **Elimina o reativo simples.**
- Estocástico → decidir por valor esperado (probabilidade × custo do erro), nova tentativa com tempo máximo.
- Episódico → **avaliação barata**: casos independentes, sem avaliar trajetória.
- Contínuo → discretização declarada: limiares de cada modo (HDF: ΔT < 8,6 K e rotação < 1380 rpm).
- Agente único e conhecido → **economizam** protocolo de comunicação e fase de exploração.

**Contra-argumentos prováveis:**

- *"Determinístico, não? A mesma leitura dá o mesmo resultado."* Não: o
  próprio dataset tem 19 falhas aleatórias (RNF) que nenhum sensor explica.
  E qualquer sistema que chama LLM tem uma ação estocástica no meio.
- *"Não é dinâmico? O desgaste aumenta com o tempo."* O desgaste aumenta com
  a máquina rodando, e na ordem de serviço ela está parada. O que cai com a
  espera é a utilidade do parecer, por isso semidinâmico.
- *"Conhecido? Você não sabe quando a máquina vai falhar."* Conhecido trata do
  que o agente **sabe das regras**, não do que ele **vê**. As regras estão
  documentadas; o que falta é observação, e isso já está em observabilidade
  parcial.

### Apresentação de 2 minutos: número de agentes

1. **Qual foi:** número de agentes. Foi a mais difícil porque há dois humanos
   no circuito: o técnico e o supervisor.
2. **Por que hesitei:** o slide diz que um humano conta se ele **reage ao que o
   agente faz**. O técnico lê o parecer e decide; parece multiagente.
3. **O que decidi:** agente único, porque o técnico age **depois** do parecer,
   e o agente não observa essa reação nem a usa na próxima ordem. Cada ordem é
   avaliada do zero. O técnico é quem recebe a decisão, não um oponente nem um
   parceiro que muda o resultado do agente.
4. **De que depende:** se a rejeição do técnico passar a realimentar o agente
   (aprender com o que ele recusou), ou se o supervisor puder vetar em tempo
   real, vira multiagente.
5. **Consequência:** hoje o projeto **não** precisa de protocolo de comunicação
   nem de prever o outro; a D11 fica periférica. Se o gatilho acontecer, ela
   vira central.

---

## Lab 03 — Formular como busca (seção 7 + `meu_problema.py`)

**Caminho padrão:** subproblema 3 do catálogo (roteiro de conformidade), com
dados do AMS. A classe `Conformidade` não foi tocada; só os dados mudaram.

**A pergunta de busca:** em que ordem o técnico confere os itens de segurança
e fecha as pendências, gastando o menor tempo.

| Componente | AMS |
|---|---|
| Estado inicial | `((), ())`: nada conferido, nenhuma pendência |
| Ações | `verificar:<item>` (não conferidos) e `resolver:<pendência>` (abertas) |
| Transição | Verificar abre pendências (painel elétrico → "desenergizar e testar tensão"); resolver fecha |
| Objetivo | Todos os 7 itens conferidos **e** nenhuma pendência aberta |
| Custo | Minutos; conferir com pendência aberta custa 2× (retrabalho) |

**Saiba dizer:**

- **O estado é a situação, não o caminho:** (itens conferidos, pendências
  abertas) em tuplas **ordenadas**. Duas ordens diferentes que chegam ao mesmo
  lugar são o mesmo estado. É a verificação 6, e ela passou.
- **Teste de sanidade:** 6 ✅ (rodar `python meu_problema.py` na pasta do lab
  para mostrar ao vivo). O espaço tem 648 estados.
- **Por que a ordem importa:** pelo retrabalho. Conferir tudo primeiro e
  resolver depois custa 107 min; a melhor ordem custa 80 min (só se descobre
  isso no lab-04, mas é o argumento de que vale formular).
- **Por que começar pelo objetivo:** foi "liberar a intervenção" que definiu o
  que o estado precisa guardar: os itens e as pendências.
- **O que NÃO é busca:** classificar o risco é classificação (D5); escolher as
  normas é regra mais recuperação (D9); recomendar o LOTO é regra.
- **Fraqueza assumida (fale antes que perguntem):** a formulação não obriga o
  LOTO a vir antes das outras conferências. A busca ótima deixa o LOTO para o
  fim, o que é aceitável só porque conferir é inspeção e não intervenção. Se a
  planta exigir bloqueio primeiro, isso vira restrição em `acoes`. É o primeiro
  ajuste no lab-04.

---

## Arquivos

- `agent-spec.md` (raiz do projeto): seções 1, 2 e 7 preenchidas; 3 a 6 ficam para os próximos encontros.
- `D2/D2-02-ambiente-em-sete-dimensoes/sete-dimensoes-perguntas.md`: o formulário respondido.
- `D2/D2-03-formular-como-busca/meu_problema.py`: a formulação.
- **Falta você:** pôr seu nome no `agent-spec.md` e fazer o commit.
