"""
rag.py — FASE 2: RAG (Retrieval-Augmented Generation)

Fluxo:  pergunta → busca trechos oficiais → monta o prompt → LLM → resposta com fontes

Rode:  python rag.py "Qual a diferença entre LRS e GRS?"
Detalhes do processo: docs/05-recuperacao-e-rag.md
"""
import sys
import time
from dataclasses import dataclass, field

from openai import OpenAI

from buscar import buscar
from config import (LLM_CHAVE, LLM_MAX_TOKENS, LLM_MODELO, LLM_TEMPERATURA, LLM_URL,
                    SIMILARIDADE_MINIMA)

cliente = OpenAI(base_url=LLM_URL, api_key=LLM_CHAVE)

# ── PROMPT DE SISTEMA: define o papel e as regras (guardrails) do tutor ──────
PROMPT_SISTEMA = """Você é o AZ-900 Tutor, um professor especialista em Microsoft Azure \
que ajuda estudantes brasileiros a passar no exame AZ-900 (Microsoft Azure Fundamentals).

REGRAS:
1. Responda SOMENTE com base nos TRECHOS OFICIAIS fornecidos. Não invente informações.
2. Cite as fontes no fim das frases, com o número do trecho entre colchetes: [1], [2]. \
Não copie a linha "Fonte:" dos trechos.
3. Se a resposta estiver nos trechos, mesmo que em partes (ex.: um trecho explica o LRS e \
outro o GRS), JUNTE as partes e responda. Só diga "Não encontrei isso na documentação \
oficial que tenho." quando NENHUM trecho tratar do assunto.
4. Responda sempre em português do Brasil, de forma didática, clara e objetiva.
5. Use exemplos simples quando ajudar.
6. Se a pergunta não for sobre Azure ou computação em nuvem, diga educadamente que você \
só ajuda com o conteúdo do AZ-900.

FORMATO:
- Comece com a resposta direta, em 1 ou 2 frases.
- Depois explique os detalhes (use tópicos se houver comparação).
- Termine com uma linha "💡 Dica para a prova:" quando for útil."""

MENSAGEM_SEM_FONTE = (
    "Não encontrei isso na documentação oficial que tenho. "
    "Tente reformular a pergunta ou usar o nome do serviço (ex.: \"Azure Policy\", \"GRS\")."
)


@dataclass
class Resultado:
    """Tudo que o tutor devolve: resposta, fontes e métricas."""
    resposta: str = ""
    fontes: list = field(default_factory=list)
    tokens_entrada: int = 0
    tokens_saida: int = 0
    segundos: float = 0.0
    modelo: str = LLM_MODELO


def recuperar(pergunta: str) -> list[dict]:
    """R do RAG: busca os trechos e descarta os pouco relevantes."""
    trechos = buscar(pergunta)
    # mantém o trecho se o significado for parecido OU se ele tiver a palavra exata (ex.: sigla "GRS")
    return [t for t in trechos if t["similaridade"] >= SIMILARIDADE_MINIMA or t.get("palavra_chave")]


def montar_contexto(trechos: list[dict]) -> str:
    """A do RAG (Augmented): transforma os trechos num bloco numerado para o LLM."""
    blocos = []
    for i, t in enumerate(trechos, 1):
        blocos.append(f"[{i}] Fonte: {t['titulo']} › {t['secao']}\n{t['texto']}")
    return "\n\n---\n\n".join(blocos)


def montar_mensagens(pergunta: str, contexto: str) -> list[dict]:
    return [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": f"TRECHOS OFICIAIS:\n\n{contexto}\n\n---\n\nPERGUNTA DO ALUNO: {pergunta}"},
    ]


def lista_fontes(trechos: list[dict]) -> list[dict]:
    return [
        {"numero": i, "titulo": t["titulo"], "secao": t["secao"], "url": t["url"],
         "area": t["area"], "similaridade": t["similaridade"]}
        for i, t in enumerate(trechos, 1)
    ]


def responder_stream(pergunta: str):
    """G do RAG (Generation), em streaming.
    Gera pedaços de texto (str) conforme o LLM escreve; no fim, gera o objeto Resultado."""
    inicio = time.time()
    trechos = recuperar(pergunta)
    res = Resultado(fontes=lista_fontes(trechos))

    if not trechos:  # guardrail: sem fonte, sem resposta inventada
        res.resposta = MENSAGEM_SEM_FONTE
        yield MENSAGEM_SEM_FONTE
        res.segundos = round(time.time() - inicio, 2)
        yield res
        return

    mensagens = montar_mensagens(pergunta, montar_contexto(trechos))
    stream = cliente.chat.completions.create(
        model=LLM_MODELO,
        messages=mensagens,
        temperature=LLM_TEMPERATURA,
        max_tokens=LLM_MAX_TOKENS,
        stream=True,
        stream_options={"include_usage": True},
    )

    partes = []
    for evento in stream:
        if evento.choices and evento.choices[0].delta.content:
            texto = evento.choices[0].delta.content
            partes.append(texto)
            yield texto
        if getattr(evento, "usage", None):
            res.tokens_entrada = evento.usage.prompt_tokens
            res.tokens_saida = evento.usage.completion_tokens

    res.resposta = "".join(partes)
    if not res.tokens_entrada:  # alguns provedores não informam: estimativa (~4 caracteres por token)
        res.tokens_entrada = sum(len(m["content"]) for m in mensagens) // 4
        res.tokens_saida = len(res.resposta) // 4
    res.segundos = round(time.time() - inicio, 2)
    yield res


def responder(pergunta: str) -> Resultado:
    """Versão sem streaming: espera a resposta completa."""
    resultado = None
    for parte in responder_stream(pergunta):
        if isinstance(parte, Resultado):
            resultado = parte
    return resultado


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Qual a diferença entre LRS e GRS?"
    print(f"\n🎓 AZ-900 Tutor  ·  modelo: {LLM_MODELO}")
    print(f"❓ {pergunta}\n")

    for parte in responder_stream(pergunta):
        if isinstance(parte, Resultado):
            r = parte
        else:
            print(parte, end="", flush=True)  # streaming: imprime conforme chega

    print("\n\n📚 Fontes:")
    for f in r.fontes:
        print(f"  [{f['numero']}] {f['titulo']} › {f['secao']}")
        print(f"      {f['url']}")
    print(f"\n📊 Tokens: {r.tokens_entrada} entrada + {r.tokens_saida} saída  ·  ⏱️ {r.segundos}s  ·  💰 US$ 0,00 (modelo local)")
