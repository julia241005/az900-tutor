"""
migrar_dados.py — Migração única do layout antigo (uma certificação) para o novo
(várias certificações, cada uma em data/<id>/...).

Antes:  data/vetores, data/fragmentos.jsonl, data/tutor.db, data/brutos, data/logs
Agora:  data/az900/vetores, data/az900/fragmentos.jsonl, data/az900/tutor.db, ...

Assim o seu progresso e o índice do AZ-900 que já existem continuam funcionando,
sem precisar baixar e indexar a documentação de novo.

Rode uma vez:  python migrar_dados.py
"""
import shutil
from pathlib import Path

import config

RAIZ = Path(__file__).parent
DADOS = RAIZ / "data"
DESTINO = config.dir_trilha("az900")

ITENS = ["vetores", "fragmentos.jsonl", "tutor.db", "brutos", "logs"]


def main():
    if not DADOS.exists():
        print("Nada a migrar: a pasta data/ ainda não existe. Rode a ingestão normalmente.")
        return

    DESTINO.mkdir(parents=True, exist_ok=True)
    movidos = 0
    for nome in ITENS:
        origem = DADOS / nome
        destino = DESTINO / nome
        if origem.exists() and not destino.exists():
            shutil.move(str(origem), str(destino))
            print(f"  ➜ data/{nome}  →  data/az900/{nome}")
            movidos += 1
        elif origem.exists() and destino.exists():
            print(f"  • pulado (já existe no destino): data/az900/{nome}")

    if movidos:
        print(f"\n✅ Migração concluída: {movidos} item(ns) movidos para data/az900/.")
        print("   O AZ-900 continua funcionando sem reindexar.")
    else:
        print("\nNada a migrar (o layout já está no formato novo ou não havia dados antigos).")


if __name__ == "__main__":
    main()
