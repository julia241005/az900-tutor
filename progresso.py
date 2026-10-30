"""
progresso.py — Desempenho do aluno por área do exame + recomendação de estudo.

Inspirado no relatório oficial de simulado da Microsoft ("desempenho por avaliação"),
usando os PESOS oficiais de cada área no exame (guia de estudo AZ-900).

Rode:  python progresso.py            (mostra o progresso da sessão "terminal")
"""
import sys
from collections import Counter

import banco
from ingestao.fontes import AREA_ARQUITETURA, AREA_CONCEITOS, AREA_GOVERNANCA

# Pesos oficiais do exame (guia de estudo AZ-900). Conferir periodicamente no guia.
PESOS = {
    AREA_CONCEITOS: "25–30%",
    AREA_ARQUITETURA: "35–40%",
    AREA_GOVERNANCA: "30–35%",
}
META = 80  # % recomendado pela Microsoft nos simulados oficiais
MINIMO_PARA_AVALIAR = 3  # respostas por área para considerar o resultado confiável


def calcular(sessao_id: str) -> dict:
    respostas = banco.respostas_do_aluno(sessao_id)
    areas = []
    for area, peso in PESOS.items():
        da_area = [r for r in respostas if r["area"] == area]
        acertos = sum(r["correta"] for r in da_area)
        total = len(da_area)
        pct = round(100 * acertos / total) if total else None
        erros = Counter((r["fonte_titulo"], r["fonte_url"]) for r in da_area if not r["correta"])
        areas.append({
            "area": area, "peso_no_exame": peso, "respostas": total, "acertos": acertos,
            "percentual": pct,
            "situacao": ("sem dados" if total == 0 else
                         "poucos dados" if total < MINIMO_PARA_AVALIAR else
                         "pronto" if pct >= META else "reforçar"),
            "revisar": [{"titulo": t, "url": u} for (t, u), _ in erros.most_common(3)],
        })

    total = len(respostas)
    acertos = sum(r["correta"] for r in respostas)
    geral = round(100 * acertos / total) if total else None
    return {
        "sessao_id": sessao_id, "respostas": total, "acertos": acertos,
        "percentual_geral": geral, "meta": META, "areas": areas,
        "recomendacao": recomendar(areas),
    }


def recomendar(areas: list[dict]) -> str:
    sem_dados = [a for a in areas if a["respostas"] < MINIMO_PARA_AVALIAR]
    if len(sem_dados) == len(areas):
        return "Faça alguns simulados para eu conseguir medir seu desempenho. Comece pela área de maior peso: Arquitetura e serviços do Azure."
    if sem_dados:
        return f"Pratique mais a área \"{sem_dados[0]['area']}\": ainda tenho poucas respostas suas nela."
    pior = min(areas, key=lambda a: a["percentual"])
    if pior["percentual"] >= META:
        return "Você está acima da meta de 80% em todas as áreas. Faça simulados completos para manter o ritmo e agende a prova!"
    texto = f"Reforce \"{pior['area']}\" ({pior['percentual']}%, peso {pior['peso_no_exame']} no exame)."
    if pior["revisar"]:
        texto += f" Comece revisando: {pior['revisar'][0]['titulo']}."
    return texto


def _barra(pct: int | None, largura: int = 20) -> str:
    if pct is None:
        return "░" * largura
    cheio = round(largura * pct / 100)
    return "█" * cheio + "░" * (largura - cheio)


def formatar(p: dict) -> str:
    if not p["respostas"]:
        return "📊 Ainda não tenho respostas suas. Peça um simulado (ex.: \"me faz um simulado de 3 perguntas\") e eu começo a medir seu progresso!"
    linhas = [f"📊 **Seu desempenho:** {p['acertos']} de {p['respostas']} ({p['percentual_geral']}%) · meta {p['meta']}%", ""]
    icones = {"pronto": "✅", "reforçar": "⚠️", "poucos dados": "🔸", "sem dados": "▫️"}
    for a in p["areas"]:
        pct = f"{a['percentual']}%" if a["percentual"] is not None else "—"
        linhas.append(f"{icones[a['situacao']]} **{a['area']}** (peso {a['peso_no_exame']})")
        linhas.append(f"   {_barra(a['percentual'])} {pct} · {a['acertos']}/{a['respostas']}")
        for r in a["revisar"][:2]:
            linhas.append(f"   📚 Revisar: [{r['titulo']}]({r['url']})")
    linhas += ["", f"🎯 **Próximo passo:** {p['recomendacao']}"]
    return "\n".join(linhas)


if __name__ == "__main__":
    print(formatar(calcular(sys.argv[1] if len(sys.argv) > 1 else "terminal")))
