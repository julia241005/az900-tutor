"""
simulado.py — Geração e correção de perguntas no estilo do exame AZ-900.

OBTER (banco primeiro): usa perguntas já APROVADAS por humano (rápido, sem IA).
GERAR (usa IA):         se faltar, sorteia trechos oficiais → o LLM cria perguntas em JSON
                        → o código valida, embaralha e salva como "pendente" para revisão.
CORRIGIR (sem IA):      comparação exata da letra com o gabarito + registro no banco.
"""
import json
import random
import re
from dataclasses import dataclass

import banco
from buscar import amostra_por_area
from config import LLM_MODELO, SIMULADO_GERAR_COM_IA
from rag import cliente, montar_contexto
from sessao import Sessao

LETRAS = ["A", "B", "C", "D"]

PROMPT_SIMULADO = """Você cria perguntas de múltipla escolha no estilo do exame Microsoft AZ-900, \
em português do Brasil, baseadas SOMENTE no trecho oficial fornecido.

Regras:
- Cada pergunta tem 4 alternativas (A, B, C, D) e apenas UMA correta.
- As alternativas erradas devem ser plausíveis (conceitos parecidos do Azure), mas claramente incorretas segundo o trecho.
- Não use detalhes que o trecho não afirma.
- A explicação diz por que a correta está certa, em 1 ou 2 frases, SEM citar letras \
(escreva o conceito, não "a opção B").

Responda APENAS com JSON válido, neste formato:
{"perguntas": [{"enunciado": "...", "alternativas": {"A": "...", "B": "...", "C": "...", "D": "..."}, \
"correta": "B", "explicacao": "..."}]}"""


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

    ordem = LETRAS[:]
    random.shuffle(ordem)                       # ordem[i] = letra antiga que vai para a posição i
    novas = {LETRAS[i]: alts[antiga] for i, antiga in enumerate(ordem)}
    de_para = {antiga: LETRAS[i] for i, antiga in enumerate(ordem)}
    nova_correta = de_para[correta]

    # A explicação pode citar letras ("a opção B..."). Depois de embaralhar, elas precisam ser
    # atualizadas para a nova posição (bug encontrado na revisão humana).
    explicacao = re.sub(
        r"\b(op[çc][ãa]o|alternativa|letra|resposta)(\s+\(?)([A-D])\b",
        lambda m: m.group(1) + m.group(2) + de_para[m.group(3)],
        str(p.get("explicacao", "")).strip(),
        flags=re.IGNORECASE,
    )

    idx = p.get("trecho", 1)
    trecho = trechos[idx - 1] if isinstance(idx, int) and 1 <= idx <= len(trechos) else trechos[0]
    return {
        "enunciado": p["enunciado"].strip(),
        "alternativas": novas,
        "correta": nova_correta,
        "explicacao": explicacao,
        "area": area or trecho["area"],
        "fonte": {"titulo": trecho["titulo"], "url": trecho["url"]},
    }


@dataclass
class Uso:
    prompt_tokens: int = 0
    completion_tokens: int = 0


def gerar_perguntas(area: str | None, quantidade: int = 3) -> tuple[list[dict], Uso]:
    """Gera perguntas. Retorna (perguntas, uso_de_tokens).
    Uma pergunta por trecho, em chamadas separadas: assim a FONTE citada é sempre
    o trecho que originou a pergunta (modelos pequenos erravam o número do trecho)."""
    uso = Uso()
    perguntas = []
    for trecho in amostra_por_area(area, quantidade):
        resp = cliente.chat.completions.create(
            model=LLM_MODELO,
            messages=[
                {"role": "system", "content": PROMPT_SIMULADO},
                {"role": "user", "content": f"TRECHO OFICIAL:\n\n{montar_contexto([trecho])}\n\nCrie 1 pergunta."},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        if resp.usage:
            uso.prompt_tokens += resp.usage.prompt_tokens or 0
            uso.completion_tokens += resp.usage.completion_tokens or 0
        dados = _extrair_json(resp.choices[0].message.content or "")
        for p in dados.get("perguntas", [])[:1]:
            p["trecho"] = 1
            if v := _validar_e_embaralhar(p, [trecho], area):
                perguntas.append(v)
    return perguntas, uso


def obter_perguntas(sessao: Sessao, area: str | None, quantidade: int = 3) -> tuple[list[dict], object]:
    """Usa o banco de perguntas aprovadas. Se SIMULADO_GERAR_COM_IA estiver ligado, a IA gera
    o que faltar e salva como 'pendente' para revisão humana (revisar_perguntas.py)."""
    ja_respondidas = {r["enunciado"] for r in banco.respostas_do_aluno(sessao.sessao_id)}
    perguntas = banco.perguntas_aprovadas(area, quantidade, evitar=ja_respondidas)
    uso = None
    faltam = quantidade - len(perguntas)
    if faltam > 0 and SIMULADO_GERAR_COM_IA:
        novas, uso = gerar_perguntas(area, faltam)
        for p in novas:
            banco.salvar_pergunta(p, status="pendente")
            p["status"] = "pendente"
        perguntas += novas
    random.shuffle(perguntas)
    return perguntas, uso


def formatar_pergunta(p: dict, numero: int, total: int) -> str:
    selo = " · 🧪 nova (em revisão)" if p.get("status") == "pendente" else ""
    linhas = [f"📝 **Pergunta {numero} de {total}** · {p['area']}{selo}", "", p["enunciado"], ""]
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
    banco.registrar_resposta(sessao.sessao_id, p, acertou)  # memória de longo prazo
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
                   "Meta para a prova: 80% ou mais. Peça \"meu progresso\" para ver seu desempenho por área."]
    return "\n".join(partes)
