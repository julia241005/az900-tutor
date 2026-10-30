"""
revisar_perguntas.py — REVISÃO HUMANA do banco de perguntas (human-in-the-loop).

A IA gera perguntas; um humano confere antes de elas virarem "oficiais".
Perguntas aprovadas são reutilizadas nos simulados (mais rápido e confiável).

Rode:  python revisar_perguntas.py              → revisa as pendentes
       python revisar_perguntas.py aprovadas    → revisa de novo as já aprovadas (corrigir engano)
Teclas: [a] aprovar · [r] rejeitar · [p] pular · [s] sair
"""
import sys

import banco

status_alvo = "aprovada" if len(sys.argv) > 1 and sys.argv[1].startswith("aprovad") else "pendente"
pendentes = banco.perguntas_por_status(status_alvo)
print(f"\n🧑‍🏫 Revisão do banco de perguntas · {len(pendentes)} {status_alvo}(s)\n")

aprovadas = rejeitadas = 0
for i, p in enumerate(pendentes, 1):
    print("=" * 70)
    print(f"[{i}/{len(pendentes)}] {p['area']}\n")
    print(p["enunciado"], "\n")
    for letra, texto in p["alternativas"].items():
        marca = "✅" if letra == p["correta"] else "  "
        print(f" {marca} {letra}) {texto}")
    print(f"\n💬 Explicação: {p['explicacao']}")
    print(f"📚 Fonte: {p['fonte']['titulo']}\n    {p['fonte']['url']}\n")
    print("Confira: a pergunta é clara? Só UMA alternativa está certa? A explicação bate com a fonte?")
    print("Dica: na dúvida, abra o link da fonte. Na dúvida que continuar, rejeite.")

    escolha = input("[a] aprovar · [r] rejeitar · [p] pular · [s] sair → ").strip().lower()
    if escolha == "a":
        banco.definir_status(p["id"], "aprovada")
        aprovadas += 1
    elif escolha == "r":
        banco.definir_status(p["id"], "rejeitada")
        rejeitadas += 1
    elif escolha == "s":
        break

print(f"\n✅ Aprovadas: {aprovadas} · ❌ Rejeitadas: {rejeitadas}")
print("\n📦 Banco de perguntas por área:")
for area, status in banco.resumo_banco().items():
    print(f"  {area}: " + ", ".join(f"{k} {v}" for k, v in status.items()))
