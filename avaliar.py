"""
avaliar.py — FASE 6: AVALIAÇÃO AUTOMÁTICA (evals).

"Funciona" não é medida. Aqui o tutor responde um conjunto fixo de perguntas
(avaliacao/conjunto.json) e o script mede, com números, se ele acerta.

  python avaliar.py                 # 1. BUSCA: compara "vetorial" x "hibrida" (rápido, sem LLM)
  python avaliar.py --completo      # 2. + RESPOSTAS: o LLM responde e o script confere (demora)
  python avaliar.py --completo --juiz   # 3. + LLM como avaliador da fidelidade (ainda mais lento)
  python avaliar.py --completo --limite 5   # só as 5 primeiras perguntas (teste rápido)

Métricas (explicadas em docs/09-avaliacao.md):
  acerto@k   → em quantas perguntas a fonte certa veio entre os k trechos
  MRR        → quão no TOPO a fonte certa veio (1 = sempre em 1º lugar)
  palavras   → % dos termos esperados que aparecem na resposta (0 se o tutor recusou)
  recusa indevida → perguntas do exame em que o tutor disse "não encontrei" sem precisar
  citação    → a resposta cita [1], [2]...?
  recusa     → nas perguntas fora do escopo, o tutor recusou em vez de inventar?

Os relatórios ficam em avaliacao/resultados/ (podem ir para o Git: não têm texto da Microsoft).
"""
import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

from buscar import _sem_acento, buscar
from config import LLM_MODELO, MODO_BUSCA, TOP_K

PASTA = Path(__file__).parent / "avaliacao"
PASTA_RESULTADOS = PASTA / "resultados"
CITACAO = re.compile(r"\[\d+\]")
SINAIS_DE_RECUSA = ("nao encontrei", "so ajudo", "apenas com", "somente com", "nao posso ajudar", "az-900")


def normalizar(t: str) -> str:
    return _sem_acento((t or "").lower())


def carregar_conjunto(limite: int | None = None) -> list[dict]:
    perguntas = json.loads((PASTA / "conjunto.json").read_text(encoding="utf-8"))["perguntas"]
    return perguntas[:limite] if limite else perguntas


def posicao_da_fonte(trechos: list[dict], fontes_esperadas: list[str]) -> int | None:
    """Em que posição (1, 2, 3...) veio o primeiro trecho da fonte certa. None = não veio."""
    for pos, t in enumerate(trechos, 1):
        if any(f in t.get("url", "") for f in fontes_esperadas):
            return pos
    return None


# ── 1. Avaliação da BUSCA ────────────────────────────────────────────────────
def avaliar_busca(perguntas: list[dict], modo: str) -> dict:
    linhas = []
    for q in perguntas:
        if q.get("fora_do_escopo"):
            continue
        inicio = time.time()
        pos = posicao_da_fonte(buscar(q["pergunta"], k=TOP_K, modo=modo), q["fontes"])
        linhas.append({"id": q["id"], "area": q["area"], "pergunta": q["pergunta"], "posicao": pos,
                       "ms": round((time.time() - inicio) * 1000)})
    n = len(linhas) or 1
    por_area = {}
    for l in linhas:
        a = por_area.setdefault(l["area"], [0, 0])
        a[0] += l["posicao"] is not None
        a[1] += 1
    return {
        "modo": modo,
        "acerto_k": round(sum(l["posicao"] is not None for l in linhas) / n, 3),
        "mrr": round(sum(1 / l["posicao"] for l in linhas if l["posicao"]) / n, 3),
        "ms_medio": round(sum(l["ms"] for l in linhas) / n),
        "por_area": {a: round(v[0] / v[1], 3) for a, v in por_area.items()},
        "falhas": [l["id"] + " · " + l["pergunta"] for l in linhas if l["posicao"] is None],
        "linhas": linhas,
    }


# ── 2. Avaliação das RESPOSTAS ───────────────────────────────────────────────
PROMPT_JUIZ = """Você é um avaliador rigoroso. Leia os TRECHOS e a RESPOSTA.
A RESPOSTA afirma apenas coisas que estão nos TRECHOS (sem inventar)?
Responda só com uma palavra: SIM ou NAO.

TRECHOS:
{contexto}

RESPOSTA:
{resposta}"""


def julgar_fidelidade(pergunta: str, resposta: str) -> bool | None:
    """LLM como avaliador (LLM-as-judge). Com um modelo pequeno, trate como indicativo, não como verdade."""
    from rag import cliente, montar_contexto, recuperar
    trechos = recuperar(pergunta)
    if not trechos:
        return None
    r = cliente.chat.completions.create(
        model=LLM_MODELO, temperature=0, max_tokens=5,
        messages=[{"role": "user", "content": PROMPT_JUIZ.format(contexto=montar_contexto(trechos), resposta=resposta)}],
    )
    return normalizar(r.choices[0].message.content).strip().startswith("sim")


def avaliar_respostas(perguntas: list[dict], juiz: bool = False) -> dict:
    from rag import responder
    linhas = []
    for i, q in enumerate(perguntas, 1):
        print(f"  [{i}/{len(perguntas)}] {q['pergunta']}", flush=True)
        r = responder(q["pergunta"])
        texto = normalizar(r.resposta)
        linha = {"id": q["id"], "area": q["area"], "pergunta": q["pergunta"], "segundos": r.segundos,
                 "tokens_entrada": r.tokens_entrada, "tokens_saida": r.tokens_saida,
                 "resposta": r.resposta[:400]}
        if q.get("fora_do_escopo"):
            linha["recusou"] = any(s in texto for s in SINAIS_DE_RECUSA)
        else:
            # recusa indevida: a pergunta é do exame, mas o tutor disse "não encontrei"
            linha["recusou_indevidamente"] = "nao encontrei" in texto
            achadas = [p for p in q["palavras"] if normalizar(p) in texto]
            linha["palavras"] = 0.0 if linha["recusou_indevidamente"] else (
                round(len(achadas) / len(q["palavras"]), 2) if q["palavras"] else 1.0)
            linha["citou"] = bool(CITACAO.search(r.resposta))
            linha["fonte_certa"] = any(any(f in fo["url"] for f in q["fontes"]) for fo in r.fontes)
            if juiz:
                linha["fiel"] = julgar_fidelidade(q["pergunta"], r.resposta)
        linhas.append(linha)

    normais = [l for l in linhas if "palavras" in l]
    fora = [l for l in linhas if "recusou" in l]
    media = lambda xs: round(sum(xs) / len(xs), 3) if xs else None
    resumo = {
        "palavras": media([l["palavras"] for l in normais]),
        "citou": media([l["citou"] for l in normais]),
        "fonte_certa": media([l["fonte_certa"] for l in normais]),
        "recusa_indevida": media([l["recusou_indevidamente"] for l in normais]),
        "recusa_fora_do_escopo": media([l["recusou"] for l in fora]),
        "segundos_medio": media([l["segundos"] for l in linhas]),
        "tokens_medio": media([l["tokens_entrada"] + l["tokens_saida"] for l in linhas]),
    }
    if juiz:
        julgadas = [l["fiel"] for l in normais if l.get("fiel") is not None]
        resumo["fiel_segundo_juiz"] = media(julgadas)
    return {"resumo": resumo, "linhas": linhas}


# ── Relatório ────────────────────────────────────────────────────────────────
pct = lambda x: "—" if x is None else f"{x * 100:.0f}%"


def relatorio_md(buscas: list[dict], respostas: dict | None, n: int) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    md = [f"# Avaliação · {agora}", "",
          f"Modelo: `{LLM_MODELO}` · TOP_K: {TOP_K} · modo em uso: `{MODO_BUSCA}` · {n} perguntas", "",
          "## Busca (a fonte certa veio entre os trechos?)", "",
          "| Modo | Acerto@k | MRR | Tempo médio |", "|---|---|---|---|"]
    md += [f"| {b['modo']} | {pct(b['acerto_k'])} | {b['mrr']} | {b['ms_medio']} ms |" for b in buscas]
    md += ["", "**Por área (acerto@k):**", ""]
    for b in buscas:
        md.append(f"- {b['modo']}: " + " · ".join(f"{a}: {pct(v)}" for a, v in b["por_area"].items()))
    for b in buscas:
        if b["falhas"]:
            md += ["", f"**Fonte não encontrada ({b['modo']}):**", ""] + [f"- {f}" for f in b["falhas"]]
    if respostas:
        r = respostas["resumo"]
        md += ["", "## Respostas", "",
               "| Métrica | Resultado |", "|---|---|",
               f"| Termos esperados presentes | {pct(r['palavras'])} |",
               f"| Cita as fontes ([1], [2]...) | {pct(r['citou'])} |",
               f"| Fonte certa entre as citadas | {pct(r['fonte_certa'])} |",
               f"| Recusa indevida (disse \"não encontrei\" numa pergunta do exame) | {pct(r['recusa_indevida'])} |",
               f"| Recusa fora do escopo | {pct(r['recusa_fora_do_escopo'])} |",
               f"| Tempo médio por resposta | {r['segundos_medio']} s |",
               f"| Tokens médios por resposta | {r['tokens_medio']} |"]
        if "fiel_segundo_juiz" in r:
            md.append(f"| Fiel aos trechos (LLM como juiz) | {pct(r['fiel_segundo_juiz'])} |")
        ruins = [l for l in respostas["linhas"]
                 if l.get("palavras", 1) < 0.5 or l.get("recusou") is False or l.get("recusou_indevidamente")]
        if ruins:
            md += ["", "**Respostas para olhar com atenção:**", ""] + [f"- {l['id']} · {l['pergunta']}" for l in ruins]
    return "\n".join(md) + "\n"


def main():
    p = argparse.ArgumentParser(description="Avaliação automática do AZ-900 Tutor")
    p.add_argument("--completo", action="store_true", help="também gera respostas com o LLM (precisa do Ollama aberto)")
    p.add_argument("--juiz", action="store_true", help="usa o LLM como avaliador de fidelidade (com --completo)")
    p.add_argument("--limite", type=int, help="avaliar só as N primeiras perguntas")
    args = p.parse_args()

    perguntas = carregar_conjunto(args.limite)
    print(f"\n📏 Avaliando {len(perguntas)} perguntas · busca: vetorial x híbrida\n")
    buscar("aquecimento")  # carrega modelo e índice antes de medir o tempo
    buscas = [avaliar_busca(perguntas, m) for m in ("vetorial", "hibrida")]
    for b in buscas:
        print(f"  {b['modo']:<9} acerto@{TOP_K}: {pct(b['acerto_k']):>4}   MRR: {b['mrr']}   ({b['ms_medio']} ms/pergunta)")

    respostas = None
    if args.completo:
        print(f"\n🧠 Gerando respostas com {LLM_MODELO} (pode levar alguns minutos)...\n")
        respostas = avaliar_respostas(perguntas, juiz=args.juiz)
        for k, v in respostas["resumo"].items():
            print(f"  {k:<24} {v}")

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    nome = datetime.now().strftime("%Y-%m-%d_%H%M") + ("_completo" if args.completo else "_busca")
    md = relatorio_md(buscas, respostas, len(perguntas))
    (PASTA_RESULTADOS / f"{nome}.md").write_text(md, encoding="utf-8")
    (PASTA_RESULTADOS / f"{nome}.json").write_text(
        json.dumps({"buscas": buscas, "respostas": respostas}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📄 Relatório: avaliacao/resultados/{nome}.md\n")


if __name__ == "__main__":
    main()
