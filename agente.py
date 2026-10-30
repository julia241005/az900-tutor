"""
agente.py — FASE 3: o AGENTE.

Diferença para o RAG da Fase 2: aqui o LLM DECIDE o que fazer.

  mensagem do aluno
        │
        ├─► é resposta de simulado (A/B/C/D)?  ──► corrige por código (sem IA)
        │
        ▼
  LLM + histórico + cartões das ferramentas  ──► decide:
        ├─ buscar_documentacao → trechos oficiais → LLM escreve a resposta (streaming)
        ├─ gerar_simulado      → perguntas (banco aprovado ou geradas) → mostradas direto ao aluno
        ├─ ver_progresso       → desempenho por área + recomendação → mostrado direto
        └─ nenhuma             → conversa simples (ex.: "oi"); se for dúvida, cai no RAG

Detalhes: docs/06-agente-e-ferramentas.md
"""
import re
import time
from dataclasses import dataclass, field

import simulado
from config import LLM_MAX_TOKENS, LLM_MODELO, LLM_TEMPERATURA
from ferramentas import FERRAMENTAS, executar
from rag import Resultado, cliente, responder_stream
from sessao import obter_sessao

PROMPT_AGENTE = """Você é o AZ-900 Tutor, um professor especialista em Microsoft Azure que ajuda \
estudantes brasileiros a passar no exame AZ-900 (Microsoft Azure Fundamentals).

Você tem ferramentas:
- buscar_documentacao: use SEMPRE para qualquer dúvida sobre Azure ou nuvem. Nunca responda \
conceitos de memória.
- gerar_simulado: use quando o aluno quiser praticar, fazer quiz, teste ou simulado.
- ver_progresso: use quando o aluno perguntar como está indo, seu desempenho ou o que estudar.

Ao responder com base nos trechos da documentação:
1. Use SOMENTE as informações dos trechos. Se não houver a resposta, diga que não encontrou \
na documentação oficial.
2. Cite as fontes com o número do trecho, por exemplo [1].
3. Português do Brasil, didático e objetivo: resposta direta primeiro, depois detalhes.
4. Quando útil, termine com "💡 Dica para a prova:".

Se o assunto não for Azure, nuvem ou o exame AZ-900, diga educadamente que você só ajuda com o AZ-900."""

RESPOSTA_SIMULADO = re.compile(r"^\s*(?:letra\s*)?\(?([A-Da-d])\)?\s*[.!]?\s*$")


@dataclass
class ResultadoAgente:
    resposta: str = ""
    tipo: str = "resposta"            # resposta | simulado | correcao | progresso | conversa
    ferramentas_usadas: list = field(default_factory=list)
    fontes: list = field(default_factory=list)
    pergunta: dict | None = None      # pergunta atual do simulado (sem gabarito), para o visual
    progresso: dict | None = None     # dados do painel de desempenho, quando pedido
    tokens_entrada: int = 0
    tokens_saida: int = 0
    segundos: float = 0.0
    modelo: str = LLM_MODELO


def _somar_uso(res: ResultadoAgente, uso):
    if uso:
        res.tokens_entrada += uso.prompt_tokens or 0
        res.tokens_saida += uso.completion_tokens or 0


def conversar_stream(sessao_id: str, mensagem: str):
    """Gera pedaços de texto conforme a resposta é produzida e, no fim, um ResultadoAgente."""
    inicio = time.time()
    sessao = obter_sessao(sessao_id)
    res = ResultadoAgente()

    def finalizar(texto: str):
        res.resposta = texto
        res.segundos = round(time.time() - inicio, 2)
        sessao.lembrar("user", mensagem)
        sessao.lembrar("assistant", texto)
        return res

    # ── Atalho determinístico: resposta a uma pergunta do simulado ───────────
    letra = RESPOSTA_SIMULADO.match(mensagem)
    if sessao.pergunta_atual and letra:
        texto = simulado.corrigir(sessao, letra.group(1))
        res.tipo = "correcao"
        res.ferramentas_usadas = ["corrigir_resposta"]
        if sessao.pergunta_atual:
            res.pergunta = {k: v for k, v in sessao.pergunta_atual.items() if k not in ("correta", "explicacao")}
        yield texto
        yield finalizar(texto)
        return

    # ── Passo 1: o LLM decide (com as ferramentas disponíveis) ──────────────
    mensagens = [{"role": "system", "content": PROMPT_AGENTE}, *sessao.historico,
                 {"role": "user", "content": mensagem}]
    decisao = cliente.chat.completions.create(
        model=LLM_MODELO, messages=mensagens, tools=FERRAMENTAS,
        temperature=0.1, max_tokens=LLM_MAX_TOKENS,
    )
    _somar_uso(res, decisao.usage)
    escolha = decisao.choices[0].message

    # ── Sem ferramenta: conversa simples ou dúvida respondida "de memória" ──
    if not escolha.tool_calls:
        if len(mensagem.split()) >= 4:
            # Guardrail: dúvidas reais sempre passam pela documentação (RAG da Fase 2)
            res.ferramentas_usadas = ["buscar_documentacao"]
            partes = []
            for parte in responder_stream(mensagem):
                if isinstance(parte, Resultado):
                    res.fontes = parte.fontes
                    res.tokens_entrada += parte.tokens_entrada
                    res.tokens_saida += parte.tokens_saida
                else:
                    partes.append(parte)
                    yield parte
            yield finalizar("".join(partes))
            return
        res.tipo = "conversa"
        texto = escolha.content or "Olá! Posso explicar conceitos do AZ-900 ou fazer um simulado com você."
        yield texto
        yield finalizar(texto)
        return

    # ── Passo 2: executar as ferramentas escolhidas ─────────────────────────
    mensagens.append({
        "role": "assistant", "content": escolha.content or "",
        "tool_calls": [{"id": c.id, "type": "function",
                        "function": {"name": c.function.name, "arguments": c.function.arguments}}
                       for c in escolha.tool_calls],
    })
    for chamada in escolha.tool_calls:
        nome = chamada.function.name
        res.ferramentas_usadas.append(nome)
        saida = executar(nome, chamada.function.arguments, sessao)
        _somar_uso(res, saida.get("uso"))

        if "exibir_direto" in saida:  # simulado/progresso → mostra direto, sem passar pelo LLM
            res.tipo = "progresso" if nome == "ver_progresso" else "simulado"
            res.pergunta = saida.get("pergunta")
            res.progresso = saida.get("progresso")
            yield saida["exibir_direto"]
            yield finalizar(saida["exibir_direto"])
            return

        res.fontes.extend(saida.get("fontes", []))
        mensagens.append({"role": "tool", "tool_call_id": chamada.id or nome, "content": saida["conteudo"]})

    # ── Passo 3: o LLM escreve a resposta final com base nos resultados (streaming) ──
    stream = cliente.chat.completions.create(
        model=LLM_MODELO, messages=mensagens, temperature=LLM_TEMPERATURA,
        max_tokens=LLM_MAX_TOKENS, stream=True, stream_options={"include_usage": True},
    )
    partes = []
    for evento in stream:
        if evento.choices and evento.choices[0].delta.content:
            partes.append(evento.choices[0].delta.content)
            yield evento.choices[0].delta.content
        _somar_uso(res, getattr(evento, "usage", None))
    yield finalizar("".join(partes))


def conversar(sessao_id: str, mensagem: str) -> ResultadoAgente:
    resultado = None
    for parte in conversar_stream(sessao_id, mensagem):
        if isinstance(parte, ResultadoAgente):
            resultado = parte
    return resultado
