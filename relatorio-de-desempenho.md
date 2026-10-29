# Relatório de desempenho da linha de base — AMS

**Projeto:** AMS · Assistente de Manutenção Segura · **Data da medição:** 28/10/2026

## 1. A métrica primária

**Captura de falha:** das ordens cujas leituras terminam em falha, a fração que o agente classificou com risco médio ou alto. Conta-se a decisão `inspecionar_antes_de_operar` como risco médio e `parar_para_manutencao` como risco alto. Limiar de sucesso: 80%. Termo contra a trapaça: alarme falso de até 15% (ordens sem falha classificadas como risco médio ou alto).

O `medir.py` imprime outra medida, o **acerto da decisão** (decisão igual ao rótulo, sobre o total). Eu reporto as duas: a primária do `agent-spec.md` é a captura, e o acerto é a medida que o script já calcula.

## 2. O valor

Saída do `python medir.py`, sobre o conjunto de reserva:

```
Métrica primária: acerto da decisão (casos com decisão igual à rotulada, sobre o total)
Valor: 25/30 = 0.8333
Conjunto: casos-de-reserva.csv — 30 casos rotulados {'seguir_operando': 16, 'parar_para_manutencao': 7, 'inspecionar_antes_de_operar': 7}
```

Pela primária do `agent-spec.md`, sobre os mesmos 30 casos (cálculo à parte, mesmas decisões):

- **Captura de falha:** 9 de 11 falhas capturadas = **81,8%** (meta: 80%).
- **Alarme falso:** 2 de 19 casos sem falha = **10,5%** (meta: 15% ou menos).

## 3. O conjunto

- **Arquivo:** `data/reserva/casos-de-reserva.csv` (versionado no repositório, com `FONTE.md`).
- **Tamanho e período:** 30 casos, lidos entre 02/03/2026 e 20/03/2026, em ordem cronológica.
- **Distribuição dos rótulos:** 16 seguir operando, 7 parar para manutenção, 7 inspecionar antes de operar.
- **Procedência:** o conjunto é **de reserva, inventado pela coordenação do curso para fim didático** (`FONTE.md`). Não é dado real da planta. O AMS usa o AI4I 2020 (sem rótulo de parecer), e o conjunto de 2.000 registros para a D5 e a D7 ainda não está rotulado. Por isso a linha de base é sobre a reserva.

## 4. Onde o agente erra

Saída do `medir.py`:

```
Onde erra (o rótulo que o agente não deu):
  caso C07: decidiu seguir_operando, correto era inspecionar_antes_de_operar
  caso C08: decidiu seguir_operando, correto era inspecionar_antes_de_operar
  caso C10: decidiu inspecionar_antes_de_operar, correto era seguir_operando
  caso C11: decidiu parar_para_manutencao, correto era inspecionar_antes_de_operar
  caso C22: decidiu parar_para_manutencao, correto era inspecionar_antes_de_operar
```

**Padrão.** Os cinco erros têm três causas diferentes. C07 e C08 são falhas que as leituras não mostram: a temperatura e a vibração estão dentro dos limiares, e o agente segue operando. C11 e C22 são o contrário: a vibração passa de 7,0 mm/s e a regra manda parar, mas o técnico só precisava inspecionar. C10 é a regra de estado sendo cautelosa demais: duas falhas recentes da família TORNO (C07 e C08) fazem a família inteira ser inspecionada por sete dias, inclusive na ordem C10, que o rótulo considera segura.

**Hipótese.** Os erros de C07 e C08 vêm da observabilidade parcial: a falha intermitente não aparece nos sensores, e a informação que decide não está na percepção do instante. Os erros de C11 e C22 vêm de um limiar binário, que não distingue "parar" de "inspecionar" numa vibração pouco acima do limite. O erro de C10 vem de uma janela de sete dias que não separa falhas da mesma família com causas diferentes.

## 5. A tabela comparativa de busca (item 4 da N2)

Problema: a formulação do laboratório 03 (ordem de conferência de segurança da OS-2026-0001, 7 itens, 4 pendências, 648 estados). Tabela dos laboratórios 04 e 05, saída do `esqueleto.py` de cada um. Os segundos variam a cada execução.

| Busca | Custo | Ações | Nós expandidos | Nós gerados | Prof. máx. | Segundos |
|---|---:|---:|---:|---:|---:|---:|
| largura | 107.0 | 11 | 2695 | 2700 | 11 | 0.0132 |
| custo_uniforme | 80.0 | 11 | 2694 | 2700 | 11 | 0.016 |
| profundidade_limitada(limite=32) | 107.0 | 11 | 12 | 11 | 11 | 0.0001 |
| aprofundamento_iterativo(limite=32) | 107.0 | 11 | 3576 | 13511 | 11 | 0.0646 |
| gulosa[admissivel] | 80.0 | 11 | 12 | 38 | 11 | 0.0004 |
| a_estrela[admissivel] | 80.0 | 11 | 1769 | 2148 | 11 | 0.0139 |
| gulosa[inadmissivel] | 80.0 | 11 | 12 | 38 | 11 | 0.0003 |
| a_estrela[inadmissivel] | 80.0 | 11 | 330 | 582 | 11 | 0.0027 |

**Pergunta: o A* admissível manteve o custo ótimo e expandiu menos que o custo uniforme?** Sim. Ambos chegam a 80 minutos, o ótimo, e o A* expandiu 1769 nós contra 2694 do custo uniforme, uma economia de 34%. A heurística admissível é o esforço mínimo de cada item e pendência que falta. Ela não estima as pendências que as verificações ainda vão abrir, e por isso não superestima.

**Ressalva de contagem.** A profundidade limitada expandiu 12 nós, mas achou um caminho de custo 107, não o ótimo: ela para no primeiro caminho que encontra. A contagem dela também é diferente, porque é recursiva e não tem fronteira; `nos_expandidos` conta entradas na recursão, sem repetidos. A parte da vantagem aparente que vem da contagem não é eficiência.

**Dominância (lab 05).** A regra de dominância vale entre duas heurísticas admissíveis: a que estima mais alto em todo estado é a que expande menos. Aqui só uma é admissível. A admissível estima o esforço mínimo que falta (38 minutos no estado inicial). A inadmissível estima o dobro disso (76 no inicial), e por isso estima mais alto em todos os 648 estados. Mas essa altura não a torna melhor: comparando com o custo real restante de cada estado, calculado por programação dinâmica, ela superestima em 542 deles. Com ela, o A* expandiu 330 nós contra 1769 da admissível, uma redução de 81%, e manteve o custo ótimo de 80 nesta instância. A economia veio sem a garantia de otimalidade. Outra formulação pode levar essa mesma estimativa a um caminho mais caro, e a tabela não mostraria isso nesta instância.
