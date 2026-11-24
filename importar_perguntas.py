"""
importar_perguntas.py — Importa os bancos de perguntas curadas de cada trilha.

Cada certificação (trilha) tem seu próprio arquivo de perguntas (perguntas/<id>.json),
que entra como "aprovadas" no banco daquela trilha (data/<id>/tutor.db).

Rode:
    python importar_perguntas.py                 # importa TODAS as trilhas que têm arquivo
    python importar_perguntas.py --trilha az900  # importa só uma trilha
"""
import argparse
import json
from pathlib import Path

import banco
import trilhas

RAIZ = Path(__file__).parent
LETRAS = {"A", "B", "C", "D"}


def importar_trilha(trilha_id: str) -> None:
    t = trilhas.obter(trilha_id)
    arquivo = RAIZ / t.perguntas_arquivo
    if not arquivo.exists():
        print(f"⚠️  {t.sigla}: arquivo {t.perguntas_arquivo} não encontrado (ainda sem perguntas) — pulando.")
        return

    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    novas = repetidas = invalidas = 0
    for p in dados.get("perguntas", []):
        valida = set(p["alternativas"]) == LETRAS and p["correta"] in LETRAS and p["fonte"]["url"]
        if not valida:
            invalidas += 1
            continue
        if banco.salvar_pergunta(p, status="aprovada", trilha=trilha_id):
            novas += 1
        else:
            repetidas += 1  # já estava no banco (mesmo enunciado)

    print(f"✅ {t.sigla}: importadas {novas} · já existentes {repetidas} · inválidas {invalidas}")
    resumo = banco.resumo_banco(trilha_id)
    for area, status in resumo.items():
        print(f"     {area}: " + ", ".join(f"{k} {v}" for k, v in status.items()))


def main(trilha_id: str = None):
    alvos = [trilha_id] if trilha_id else [t.id for t in trilhas.listar()]
    for tid in alvos:
        importar_trilha(tid)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Importa as perguntas curadas das trilhas para o banco.")
    ap.add_argument("--trilha", default=None, help="id da trilha (padrão: todas).")
    main(ap.parse_args().trilha)
