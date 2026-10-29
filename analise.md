# Análise da linha de base — o que torna o problema difícil

## O que torna o problema difícil

Três propriedades do ambiente pesam sobre a decisão, e cada uma aparece nos números.

**Observabilidade parcial.** A linha de base perdeu C07 e C08: duas falhas em que as leituras estavam dentro dos limiares e o agente seguiu operando. A informação que decide não está na percepção do instante. Só o histórico da família mostra o padrão, e ainda assim não separa falhas de causas diferentes, como o erro de C10 mostra.

**Ordem das verificações.** Na formulação do laboratório 03, a ordem de conferência muda o custo. Conferir tudo antes de resolver as pendências custa 107 minutos; a melhor ordem custa 80. A busca de custo uniforme expandiu 2694 nós para achar a melhor ordem, e o A* com a heurística admissível, 1769 nós, sem perder o ótimo. A heurística precisava de um fato que o agente tem, o esforço mínimo de cada item, mas não tem o da pendência que o item vai abrir.

**Limiar binário.** C11 e C22 mostram o problema de decidir entre "parar" e "inspecionar" com um corte único de vibração. Os dois casos estão a pouco do limite de 7,0 mm/s, e a regra não tem gradação para eles.

## Que tipo de agente o problema realmente exige

Regra simples não basta: a janela de sete dias e a observabilidade parcial exigem estado interno, e foi isso que a linha de base usou. O agente precisa de memória das falhas por família, com política de esquecimento, e isso dispensa um modelo de aprendizado para a primeira versão.

Busca entra em outro ponto: na ordem das verificações de segurança antes da intervenção, não no parecer. Usar busca no parecer seria pagar custo de planejamento sem ganho, porque a decisão de risco não depende de sequência. Por isso o tipo é baseado em modelo, e a busca fica restrita ao roteiro.

A escolha obriga o projeto a manter o estado de falhas por família e a registrá-lo para auditoria. Dispensa planejamento de trajetória (a avaliação é por casos independentes) e protocolo com outros agentes, porque o técnico reage ao parecer só depois dele.

## O que isto muda no projeto

A D10 precisa trazer dois dados que a linha de base não tem: o histórico de intervenções da máquina, que explicaria as falhas de C07 e C08, e uma gradação de risco no lugar do limiar único, que resolveria C11 e C22. A linha de base é competitiva na captura, 81,8% contra a meta de 80%, com alarme falso de 10,5%, e isso é informação: sobre a reserva, regras e estado já resolvem a maior parte, e o modelo tem que ganhar nos casos que as regras erram. Com o conjunto de reserva inventado, o número ainda não se generaliza para a planta.
