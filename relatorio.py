"""
relatorio.py — OBSERVABILIDADE + FINOPS: o que aconteceu e quanto custaria.

Lê data/logs/interacoes.jsonl e mostra:
  - quantas perguntas, erros e de que tipo (resposta, simulado, progresso...)
  - tempo médio e p95 (o tempo que 95% das respostas não ultrapassam)
  - ferramentas mais usadas pelo agente
  - tokens e CUSTO: real (zero, modelo local) x referência numa API paga

  python relatorio.py            # todo o histórico
  python relatorio.py --dias 7   # só os últimos 7 dias

Detalhes: docs/10-custo.md
"""
import argparse
from collections import Counter
from datetime import datetime, timedelta

from config import PRECO_REF_ENTRADA_1M, PRECO_REF_SAIDA_1M
from observabilidade import custo_referencia, ler_eventos


def percentil(valores: list[float], p: float) -> float:
    if not valores:
        return 0.0
    v = sorted(valores)
    return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]


def resumir(eventos: list[dict]) -> dict:
    ok = [e for e in eventos if not e.get("erro")]
    tempos = [e.get("segundos", 0) for e in ok]
    entrada = sum(e.get("tokens_entrada", 0) for e in ok)
    saida = sum(e.get("tokens_saida", 0) for e in ok)
    com_ia = [e for e in ok if e.get("tokens_entrada", 0) + e.get("tokens_saida", 0) > 0]
    custo = custo_referencia(entrada, saida)
    sessoes = {e.get("sessao") for e in ok if e.get("sessao")}
    return {
        "interacoes": len(eventos),
        "erros": len(eventos) - len(ok),
        "por_tipo": Counter(e.get("tipo", "?") for e in ok),
        "ferramentas": Counter(f for e in ok for f in e.get("ferramentas", [])),
        "sem_fonte": sum(1 for e in ok if e.get("tipo") == "resposta" and e.get("fontes") == 0),
        "tempo_medio": round(sum(tempos) / len(tempos), 2) if tempos else 0,
        "tempo_p95": round(percentil(tempos, 95), 2),
        "tokens_entrada": entrada,
        "tokens_saida": saida,
        "custo_ref_total": custo,
        "custo_ref_por_pergunta": custo / len(com_ia) if com_ia else 0,
        "custo_ref_por_aluno": custo / len(sessoes) if sessoes else 0,
        "alunos": len(sessoes),
    }


def main():
    p = argparse.ArgumentParser(description="Relatório de uso e custo do AZ-900 Tutor")
    p.add_argument("--dias", type=int, help="considerar só os últimos N dias")
    args = p.parse_args()

    eventos = ler_eventos()
    if args.dias:
        corte = (datetime.now() - timedelta(days=args.dias)).isoformat()
        eventos = [e for e in eventos if e.get("quando", "") >= corte]
    if not eventos:
        print("\nAinda não há interações registradas. Use o tutor e rode de novo.\n")
        return

    r = resumir(eventos)
    print("\n📊 AZ-900 Tutor · relatório de uso" + (f" (últimos {args.dias} dias)" if args.dias else ""))
    print(f"\n  Interações: {r['interacoes']}   ·   erros: {r['erros']}   ·   alunos (sessões): {r['alunos']}")
    print("  Por tipo:   " + "  ".join(f"{t}: {n}" for t, n in r["por_tipo"].most_common()))
    if r["ferramentas"]:
        print("  Ferramentas: " + "  ".join(f"{t}: {n}" for t, n in r["ferramentas"].most_common()))
    print(f"  Respostas sem fonte (tutor disse 'não encontrei'): {r['sem_fonte']}")
    print(f"\n⏱️  Tempo médio: {r['tempo_medio']} s   ·   p95: {r['tempo_p95']} s")
    print(f"\n💰 Tokens: {r['tokens_entrada']:,} entrada + {r['tokens_saida']:,} saída".replace(",", "."))
    print("   Custo real: US$ 0,00 (modelo local no seu computador)")
    print(f"   Custo de referência numa API paga (US$ {PRECO_REF_ENTRADA_1M}/1M entrada, US$ {PRECO_REF_SAIDA_1M}/1M saída):")
    print(f"     total US$ {r['custo_ref_total']:.4f} · por pergunta US$ {r['custo_ref_por_pergunta']:.5f}"
          f" · por aluno US$ {r['custo_ref_por_aluno']:.4f}")
    if r["custo_ref_por_pergunta"]:
        print(f"     → 1.000 perguntas custariam cerca de US$ {r['custo_ref_por_pergunta'] * 1000:.2f}")
    print()


if __name__ == "__main__":
    main()
