"""
gerar_banco.py — Gera perguntas em lote para o banco (ficam "pendentes" até a revisão).

Ideal para rodar com calma (ex.: deixar gerando enquanto estuda) e depois revisar.

Rode:  python gerar_banco.py              → 3 perguntas por área
       python gerar_banco.py 5            → 5 perguntas por área
Depois: python revisar_perguntas.py
"""
import sys
import time

import banco
from ferramentas import AREAS
from simulado import gerar_perguntas

por_area = int(sys.argv[1]) if len(sys.argv) > 1 else 3
LOTE = 2  # perguntas por chamada ao LLM (lotes pequenos funcionam melhor em modelos pequenos)

total = 0
for area in AREAS:
    print(f"\n📘 {area}")
    criadas = 0
    tentativas = 0
    while criadas < por_area and tentativas < por_area * 2:
        tentativas += 1
        inicio = time.time()
        perguntas, _ = gerar_perguntas(area, min(LOTE, por_area - criadas))
        for p in perguntas:
            if banco.salvar_pergunta(p, status="pendente"):
                criadas += 1
                print(f"  ✅ {p['enunciado'][:80]}")
        print(f"     ⏱️ {time.time() - inicio:.0f}s")
    total += criadas

print(f"\n🧪 {total} pergunta(s) nova(s) aguardando revisão. Rode: python revisar_perguntas.py")
