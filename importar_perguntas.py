"""
importar_perguntas.py — Importa o banco de perguntas curadas (perguntas/curadas.json).

As perguntas curadas foram escritas com base na trilha oficial do Microsoft Learn,
com fonte citada, e entram como "aprovadas". Você pode revisá-las quando quiser:
    python revisar_perguntas.py aprovadas

Rode:  python importar_perguntas.py
"""
import json
from pathlib import Path

import banco

ARQUIVO = Path(__file__).parent / "perguntas" / "curadas.json"
LETRAS = {"A", "B", "C", "D"}

dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
novas = repetidas = invalidas = 0

for p in dados["perguntas"]:
    valida = set(p["alternativas"]) == LETRAS and p["correta"] in LETRAS and p["fonte"]["url"]
    if not valida:
        invalidas += 1
        continue
    if banco.salvar_pergunta(p, status="aprovada"):
        novas += 1
    else:
        repetidas += 1  # já estava no banco (mesmo enunciado)

print(f"✅ Importadas: {novas} · já existentes: {repetidas} · inválidas: {invalidas}")
print("\n📦 Banco de perguntas por área:")
for area, status in banco.resumo_banco().items():
    print(f"  {area}: " + ", ".join(f"{k} {v}" for k, v in status.items()))
