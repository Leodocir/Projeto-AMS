"""Laboratório 03 — AMS: o roteiro de segurança antes da intervenção.

Caminho padrão: subproblema 3 do catálogo (`comum/problemas/conformidade.py`)
com os dados do AMS. A classe `Conformidade` é usada sem alteração; só os
dados mudaram.

A pergunta de busca: **em que ordem o técnico confere os itens de segurança
de uma ordem de serviço e fecha as pendências que eles abrem**, gastando o
menor tempo possível e terminando com o roteiro completo e nenhuma pendência
aberta.

O caso é uma ordem fixa, a mesma do README-API:
    OS-2026-0001 · máquina M14860 (tipo M)
    "Troca do insert de corte do eixo 3 e regulagem da folga."

Os cinco componentes:
  - Estado inicial: ((), ()), nenhum item conferido e nenhuma pendência aberta.
  - Ações: "verificar:<item>" para cada item ainda não conferido e
    "resolver:<pendência>" para cada pendência aberta.
  - Transição: verificar soma o item aos conferidos e abre as pendências que
    ele revela; resolver tira a pendência das abertas.
  - Teste de objetivo: todos os itens do roteiro conferidos E nenhuma
    pendência aberta. É a condição para liberar a intervenção.
  - Custo: minutos do técnico. Conferir um item com pendência aberta custa o
    dobro (fator_retrabalho = 2.0): conferir com a máquina ainda energizada
    ou sem proteção obriga a reconferir depois do bloqueio.

O estado é o par (itens conferidos, pendências abertas), cada um como tupla
ORDENADA. Guarda a situação e não a ordem em que as coisas foram feitas.

Teste de sanidade (desta pasta):
    python verificar-formulacao.py meu_problema.py:MEU_PROBLEMA
ou simplesmente:
    python meu_problema.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Acha a pasta comum/ (motor + catálogo), igual ao verificar-formulacao.py.
_AQUI = Path(__file__).resolve().parent
for _pasta in (_AQUI, *_AQUI.parents):
    if (_pasta / "comum" / "problemas" / "conformidade.py").is_file():
        if str(_pasta / "comum") not in sys.path:
            sys.path.insert(0, str(_pasta / "comum"))
        break

from problemas.conformidade import Conformidade, Item  # noqa: E402

# --------------------------------------------------------------------------
# Dados do AMS (os únicos itens trocados em relação ao catálogo)
# --------------------------------------------------------------------------
# Item(nome, esforço em MINUTOS, pendências que conferir este item abre
# NESTE caso). O caso é fixo: uma troca de ferramenta de corte numa
# máquina com painel elétrico ao lado e sem trabalho em altura.

ITENS_AMS: tuple[Item, ...] = (
    Item("conferir a leitura atual dos sensores (risco de falha)", 3.0),
    Item("identificar as fontes de energia da máquina (NR-12)", 8.0,
         ("aplicar bloqueio e etiquetagem (LOTO)",)),
    Item("verificar o painel elétrico no ponto de intervenção (NR-10)", 10.0,
         ("desenergizar e testar a ausência de tensão",)),
    Item("verificar proteções móveis e intertravamentos (NR-12)", 6.0,
         ("instalar proteção provisória na zona de corte",)),
    Item("conferir se há trabalho acima de 2 m (NR-35)", 2.0),
    Item("conferir o EPI da equipe para troca de ferramenta de corte", 4.0,
         ("fornecer luva anticorte",)),
    Item("confirmar a ferramenta de reposição e o torque de aperto", 5.0),
)

PENDENCIAS_AMS: dict[str, float] = {
    "aplicar bloqueio e etiquetagem (LOTO)": 15.0,
    "desenergizar e testar a ausência de tensão": 12.0,
    "instalar proteção provisória na zona de corte": 10.0,
    "fornecer luva anticorte": 5.0,
}

MEU_PROBLEMA = Conformidade(ITENS_AMS, PENDENCIAS_AMS, fator_retrabalho=2.0)


if __name__ == "__main__":
    import importlib.util

    teste = importlib.util.spec_from_file_location(
        "verificar-formulacao", _AQUI / "verificar-formulacao.py")
    modulo = importlib.util.module_from_spec(teste)
    sys.modules["verificar-formulacao"] = modulo
    teste.loader.exec_module(modulo)
    raise SystemExit(modulo.main([str(Path(__file__)) + ":MEU_PROBLEMA"]))
