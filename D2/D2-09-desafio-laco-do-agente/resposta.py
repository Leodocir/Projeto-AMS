"""Desafio — o laço do agente, à mão: percepção → decisão → ação.

Este é o resposta.py: os TODOs do esqueleto, preenchidos.

O desafio inteiro é um laço que você já viu duas vezes (as demonstrações);
o que falta aqui é escrevê-lo SEM arcabouço pronto — é exatamente a peça
que a D10 vai construir com framework. Três compromissos do projeto:

  1. A chamada de ferramenta é no formato ESTRUTURADO NATIVO do modelo
     (functionDeclarations, no REST do Gemini) — nada de instruir o modelo
     a escrever "Ação:" e caçar a palavra com expressão regular: o padrão
     de 2023 é frágil e não se usa mais.
  2. A execução é MANUAL: o modelo devolve um pedido de função e QUEM
     executa é o seu laço. No REST direto não existe executor automático
     de SDK — se você optar por um SDK, descubra e DESLIGUE o executor
     automático dele; o desafio perde a razão de existir com execução
     automática.
  3. TETO DE RODADAS: o laço para no limite e diz por quê — deliberar sem
     teto é o que o bloco B3 do E4 chamou de irracional (racionalidade
     limitada: pensar custa tokens, tempo e dinheiro).

Modo SEM REDE: `python resposta.py --sem-rede` roda o laço contra as
respostas gravadas em `respostas-sem-rede.json` — zero requisições, zero
cota. O modo real usa a SUA chave do ambiente (GEMINI_API_KEY — veja o
material da D1 para criar a sua); a chave nunca fica em arquivo do projeto.

No fim, o laço GRAVA o seu próprio rastro no mesmo formato das
demonstrações — encene-o:

    python encenar.py rastro-do-laco.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
MODELO_PADRAO = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
AQUI = Path(__file__).resolve().parent

# O caso é o das demonstrações — a turma reconhece e olha o mecanismo.
PEDIDO = (
    "OS-2026-0042 · máquina L14720 (torno, linha 2) · intervenção prevista: "
    "substituição do rolamento do mancal dianteiro e alinhamento · leitura "
    "atual: vibração 6,8 mm/s, temperatura do mancal 71 °C · Decida e "
    "registre a recomendação: liberar para operação, inspecionar antes de "
    "operar, ou parar para manutenção."
)

REGISTRO_DE_MAQUINAS = {
    "L14720": {
        "ultima_manutencao": "2026-03-09 (214 dias atrás)",
        "pendencias_abertas": [
            "alinhamento do mancal dianteiro — achado confirmado na "
            "inspeção de 12/09, sem intervenção desde então"
        ],
        "vibracao_ultimas_leituras_mm_s": [4.1, 4.6, 5.3, 6.1, 6.8],
        "observacao": "tendência de alta consistente nas últimas cinco "
                      "leituras",
    }
}

INSTRUCAO = (
    "Você é o agente de manutenção da planta. Para recomendar, consulte "
    "SEMPRE o registro da máquina antes de decidir — não decida de "
    "memória. Ao decidir, registre a recomendação na ordem com a "
    "justificativa, e responda em português, em um parágrafo curto."
)

# TODO 1: o registro de ferramentas no formato nativo (functionDeclarations).
# Duas ferramentas — as mesmas das demonstrações:
#   - consultar_registro(maquina: str) — leitura;
#   - registrar_recomendacao(ordem, recomendacao, justificativa) — escrita,
#     com recomendacao num dos três valores fechados.
# Cada declaração leva name, description e parameters
# (type OBJECT/STRING, properties, required).
FERRAMENTAS: list[dict] = [
    {
        "name": "consultar_registro",
        "description": ("Consulta o registro da máquina: última manutenção, "
                        "pendências abertas, últimas leituras de vibração "
                        "e observação. Leitura, sem efeito no mundo."),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "maquina": {"type": "STRING",
                            "description": "Identificador da máquina, ex.: L14720"},
            },
            "required": ["maquina"],
        },
    },
    {
        "name": "registrar_recomendacao",
        "description": ("Registra a recomendação do agente na ordem de "
                        "serviço, com a justificativa. Escrita: deixa "
                        "registro no histórico da ordem."),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ordem": {"type": "STRING",
                          "description": "Identificador da ordem de serviço"},
                "recomendacao": {
                    "type": "STRING",
                    "enum": ["liberar_para_operacao",
                             "inspecionar_antes_de_operar",
                             "parar_para_manutencao"],
                },
                "justificativa": {"type": "STRING",
                                  "description": "Por que essa recomendação"},
            },
            "required": ["ordem", "recomendacao", "justificativa"],
        },
    },
]


def executar_ferramenta(nome: str, argumentos: dict) -> dict:
    """Quem executa é o SEU código — o modelo só pediu."""
    if nome == "consultar_registro":
        registro = REGISTRO_DE_MAQUINAS.get(argumentos.get("maquina", ""))
        return dict(registro) if registro else \
            {"erro": f"máquina sem registro: {argumentos}"}
    if nome == "registrar_recomendacao":
        return {
            "status": "registrada",
            "quando": "2026-10-09T09:41:00",
            "por": "agente-manutencao",
            "ordem": argumentos.get("ordem", ""),
        }
    return {"erro": f"ferramenta desconhecida: {nome}"}


def chamar_com_rede(modelo: str, chave: str, contents: list,
                    ferramentas: list) -> dict:
    """Uma requisição generateContent (REST direto, biblioteca padrão).

    Devolve um dicionário simples: {"functionCall": {...}} ou
    {"text": "..."}. A parte com functionCall tem que ser guardada INTEIRA
    para voltar na mensagem seguinte — os modelos com raciocínio exigem o
    thoughtSignature de volta.
    """
    # TODO 2: montar o corpo (contents + systemInstruction + tools),
    # chamar {URL_BASE}/{modelo}:generateContent com a chave no cabeçalho
    # x-goog-api-key (urllib.request, biblioteca padrão) e TRADUZIR a
    # resposta: parte com functionCall → {"functionCall": ...};
    # senão, junte as partes de texto → {"text": ...}.
    corpo = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": INSTRUCAO}]},
        "tools": [{"functionDeclarations": ferramentas}],
    }
    requisicao = urllib.request.Request(
        f"{URL_BASE}/{modelo}:generateContent",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "x-goog-api-key": chave},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=60) as resposta_http:
        dados = json.loads(resposta_http.read().decode("utf-8"))
    partes = dados["candidates"][0]["content"]["parts"]
    for parte in partes:
        if "functionCall" in parte:
            # a parte INTEIRA volta na rodada seguinte (thoughtSignature)
            return {"functionCall": parte["functionCall"], "parte": parte}
    return {"text": "".join(p.get("text", "") for p in partes)}


def chamar_sem_rede(conteudos: list, ferramentas: list) -> dict:
    """A resposta 'do modelo' vem da lista gravada — zero requisições."""
    del conteudos, ferramentas        # o modo sem rede não olha o contexto
    if not _SEM_REDE["respostas"]:
        raise RuntimeError(
            "as respostas gravadas acabaram — o laço pediu mais chamadas "
            "do que o roteiro tem; aumente o roteiro ou confira o laço")
    return _SEM_REDE["respostas"].pop(0)


_SEM_REDE: dict = {"respostas": []}


def laco(pedido: str, teto: int, chamar) -> dict:
    """O laço inteiro: percepção → decisão → ação → observação → repete.

    Roda até o modelo responder sem pedir ferramenta, ou até o TETO —
    e registra cada rodada no MESMO formato dos rastros das demonstrações
    (invérte com: python encenar.py rastro-do-laco.json).
    """
    contents = [{"role": "user", "parts": [{"text": pedido}]}]
    rodadas: list[dict] = []
    resposta_final = None

    for numero in range(1, teto + 1):
        resposta = chamar(contents, FERRAMENTAS)

        if "text" in resposta:
            # TODO 3 (a): resposta sem pedido de ferramenta — o laço termina.
            rodadas.append({
                "numero": numero,
                "invoke_agent": {
                    "entrada_da_rodada": "texto final pedido ao modelo",
                    "historico_acumulado": [pedido],
                    "registro_de_ferramentas":
                        [f.get("name") for f in FERRAMENTAS],
                },
                "raciocinio": "",
                "execute_tool": None,
                "usage": {"promptTokenCount": 0,
                          "candidatesTokenCount": 0,
                          "totalTokenCount": 0},
            })
            resposta_final = {"rodada": numero, "texto": resposta["text"]}
            break

        # Uma rodada: o modelo pediu uma ferramenta; QUEM executa é o laço.
        nome = resposta["functionCall"]["name"]
        argumentos = resposta["functionCall"].get("args", {})
        retorno = executar_ferramenta(nome, argumentos)

        # A parte do modelo volta INTEIRA (com thoughtSignature, se veio).
        parte_do_modelo = resposta.get(
            "parte", {"functionCall": resposta["functionCall"]})
        contents.append({"role": "model", "parts": [parte_do_modelo]})
        contents.append({"role": "user", "parts": [{
            "functionResponse": {"name": nome, "response": retorno}}]})

        rodadas.append({
            "numero": numero,
            "invoke_agent": {
                "entrada_da_rodada": "pedido do laço ao modelo",
                "historico_acumulado": [pedido],
                "registro_de_ferramentas":
                    [f.get("name") for f in FERRAMENTAS],
            },
            "raciocinio": "",
            "execute_tool": {
                "chamada": {"nome": nome, "argumentos": argumentos},
                "retorno": retorno,
            },
            "usage": {"promptTokenCount": 0,
                      "candidatesTokenCount": 0,
                      "totalTokenCount": 0},
        })

    if resposta_final is None:
        print(f"TETO DE RODADAS atingido ({teto}): o laço não convergiu. "
              "Deliberar sem teto é irracional — pensar custa tokens, "
              "tempo e dinheiro (bloco B3 do E4).")

    return {
        "demonstracao": "rastro do desafio-laco-do-agente (o seu laço)",
        "dominio": "manutenção industrial — OS-2026-0042, L14720",
        "modelo": MODELO_PADRAO,
        "pedido_inicial": pedido,
        "ferramentas": [
            {"nome": f.get("name", "?"),
             "tipo": "leitura" if f.get("name") == "consultar_registro"
             else "escrita"}
            for f in FERRAMENTAS
        ],
        "teto_de_rodadas": teto,
        "rodadas": rodadas,
        "resposta_final": resposta_final,
        "termino": "resposta_final" if resposta_final else "teto_de_rodadas",
    }


def principal() -> int:
    leitor = argparse.ArgumentParser(
        description="O laço do agente, à mão (desafio opcional).")
    leitor.add_argument("--teto", type=int, default=6)
    leitor.add_argument("--sem-rede", action="store_true",
                        help="roda contra respostas-sem-rede.json — zero "
                             "requisições, zero cota")
    leitor.add_argument("--saida", default="rastro-do-laco.json",
                        help="onde gravar o rastro do seu laço")
    argumentos = leitor.parse_args()

    if not FERRAMENTAS:
        print("ERRO: FERRAMENTAS está vazio — TODO 1.", file=sys.stderr)
        return 1

    chamar = chamar_sem_rede
    if argumentos.sem_rede:
        roteiro = AQUI / "respostas-sem-rede.json"
        _SEM_REDE["respostas"] = json.loads(
            roteiro.read_text(encoding="utf-8"))["respostas"]
        print("Modo SEM REDE: as respostas vêm do roteiro gravado "
              f"({roteiro.name}) — nenhuma requisição será feita.")
    else:
        chave = os.environ.get("GEMINI_API_KEY", "")
        if not chave:
            print("ERRO: GEMINI_API_KEY não está no ambiente.", file=sys.stderr)
            print("O que fazer: use --sem-rede para rodar sem cota, ou "
                  "exporte a SUA chave (como você fez na D1 — o material "
                  "dela ensina a criar; a chave nunca fica em arquivo do "
                  "projeto).", file=sys.stderr)
            return 1

        def chamar(contents, ferramentas):        # noqa: F811
            return chamar_com_rede(MODELO_PADRAO, chave, contents,
                                   ferramentas)

    rastro = laco(PEDIDO, argumentos.teto, chamar)
    Path(argumentos.saida).write_text(
        json.dumps(rastro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    rodadas = len(rastro["rodadas"])
    fim = "resposta final" if rastro["resposta_final"] else "TETO"
    print(f"Rastro gravado em {argumentos.saida}: {rodadas} rodada(s), "
          f"termino={fim}.")
    print(f"Encene o seu laço:  python encenar.py {argumentos.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
