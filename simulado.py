"""
simulado.py — Geração e correção de perguntas no estilo do exame AZ-900.

GERAR  (usa IA):     sorteia trechos oficiais da área → o LLM cria perguntas em JSON
                     → o código valida e embaralha as alternativas.
CORRIGIR (sem IA):   comparação exata da letra escolhida com o gabarito.
                     Correção não pode "alucinar", então é feita por código.
"""
import json
import random
import re

from buscar import amostra_por_area
from config import LLM_MODELO
from rag import cliente, montar_contexto
from sessao import Sessao

LETRAS = ["A", "B", "C", "D"]

PROMPT_SIMULADO = """Você cria perguntas de múltipla escolha no estilo do exame Microsoft AZ-900, \
em português do Brasil, baseadas SOMENTE nos trechos oficiais fornecidos.

Regras:
- Cada pergunta tem 4 alternativas (A, B, C, D) e apenas UMA correta.
- As alternativas erradas devem ser plausíveis (conceitos parecidos do Azure).
- A explicação diz por que a correta está certa, em 1 ou 2 frases.
- "trecho" é o número do trecho usado como base.

Responda APENAS com JSON válido, neste formato:
{"perguntas": [{"enunciado": "...", "alternativas": {"A": "...", "B": "...", "C": "...", "D": "..."}, \
"correta": "B", "explicacao": "...", "trecho": 1}]}"""


def _extrair_json(texto: str) -> dict:
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        achado = re.search(r"\{.*\}", texto, re.DOTALL)  # modelos pequenos às vezes escrevem algo antes/depois
        return json.loads(achado.group(0)) if achado else {}


def _validar_e_embaralhar(p: dict, trechos: list[dict], area: str | None) -> dict | None:
    """Garante o formato certo e embaralha as alternativas (evita que a correta seja sempre 'A')."""
    alts = p.get("alternativas") or {}
    correta = str(p.get("correta", "")).strip().upper()[:1]
    if not p.get("enunciado") or set(alts) != set(LETRAS) or correta not in LETRAS:
        return None

    texto_correto = alts[correta]
    textos = [alts[l] for l in LETRAS]
    random.shuffle(textos)
    novas = dict(zip(LETRAS, textos))
    nova_correta = LETRAS[textos.index(texto_correto)]

    idx = p.get("trecho", 1)
    trecho = trechos[idx - 1] if isinstance(idx, int) and 1 <= idx <= len(trechos) else trechos[0]
    return {
        "enunciado": p["enunciado"].strip(),
        "alternativas": novas,
        "correta": nova_correta,
        "explicacao": str(p.get("explicacao", "")).strip(),
        "area": area or trecho["area"],
        "fonte": {"titulo": trecho["titulo"], "url": trecho["url"]},
    }


def gerar_perguntas(area: str | None, quantidade: int = 3) -> tuple[list[dict], object]:
    """Gera perguntas. Retorna (perguntas, uso_de_tokens)."""
    trechos = amostra_por_area(area, max(2, quantidade))
    if not trechos:
        return [], None
    resp = cliente.chat.completions.create(
        model=LLM_MODELO,
        messages=[
            {"role": "system", "content": PROMPT_SIMULADO},
            {"role": "user", "content": f"TRECHOS OFICIAIS:\n\n{montar_contexto(trechos)}\n\n"
                                        f"Crie {quantidade} pergunta(s)."},
        ],
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    dados = _extrair_json(resp.choices[0].message.content or "")
    perguntas = [v for p in dados.get("perguntas", []) if (v := _validar_e_embaralhar(p, trechos, area))]
    return perguntas[:quantidade], resp.usage


def formatar_pergunta(p: dict, numero: int, total: int) -> str:
    linhas = [f"📝 **Pergunta {numero} de {total}** · {p['area']}", "", p["enunciado"], ""]
    linhas += [f"**{l})** {p['alternativas'][l]}" for l in LETRAS]
    linhas += ["", "Responda com a letra (A, B, C ou D)."]
    return "\n".join(linhas)


def iniciar(sessao: Sessao, perguntas: list[dict]) -> str:
    sessao.simulado = perguntas[1:]
    sessao.pergunta_atual = perguntas[0]
    sessao.acertos_rodada, sessao.total_rodada = 0, len(perguntas)
    return formatar_pergunta(perguntas[0], 1, len(perguntas))


def corrigir(sessao: Sessao, letra: str) -> str:
    """Correção determinística + próxima pergunta ou placar final."""
    p = sessao.pergunta_atual
    acertou = letra.upper() == p["correta"]
    sessao.resultados.append({"area": p["area"], "correta": acertou})
    if acertou:
        sessao.acertos_rodada += 1

    partes = [
        "✅ **Correto!**" if acertou else f"❌ **Não foi dessa vez.** A resposta certa é **{p['correta']}**.",
        "",
        p["explicacao"],
        f"📚 Fonte: [{p['fonte']['titulo']}]({p['fonte']['url']})",
    ]

    if sessao.simulado:
        sessao.pergunta_atual = sessao.simulado.pop(0)
        numero = sessao.total_rodada - len(sessao.simulado)
        partes += ["", "---", "", formatar_pergunta(sessao.pergunta_atual, numero, sessao.total_rodada)]
    else:
        sessao.pergunta_atual = None
        pct = round(100 * sessao.acertos_rodada / sessao.total_rodada)
        partes += ["", "---", "",
                   f"🏁 **Fim do simulado:** {sessao.acertos_rodada} de {sessao.total_rodada} ({pct}%).",
                   "Meta para a prova: 80% ou mais. Quer outra rodada ou revisar algum tema?"]
    return "\n".join(partes)
