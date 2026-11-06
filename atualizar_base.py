"""
atualizar_base.py — ROTINA DE ATUALIZAÇÃO da base de conhecimento.

A documentação da Microsoft muda. Este script repete o pipeline inteiro
(coletar → fragmentar → indexar) e mostra O QUE MUDOU desde a última coleta.

  python atualizar_base.py

Depois de rodar:
  1. feche e abra o tutor de novo (ele carrega o índice novo ao iniciar)
  2. rode  python avaliar.py  para conferir se a qualidade da busca se manteve

Sugestão: rodar uma vez por mês ou quando a Microsoft anunciar mudanças no exame.
Detalhes: docs/08-atualizacao.md
"""
import hashlib
import json
import time

from config import PASTA_BRUTOS


def fotografia() -> dict[str, str]:
    """url → impressão digital (hash) do texto de cada página já baixada."""
    paginas = {}
    for arq in PASTA_BRUTOS.glob("*.json"):
        doc = json.loads(arq.read_text(encoding="utf-8"))
        paginas[doc["url"]] = hashlib.sha256(doc["texto"].encode("utf-8")).hexdigest()
    return paginas


def main():
    inicio = time.time()
    antes = fotografia() if PASTA_BRUTOS.exists() else {}
    print(f"\n🔄 Atualizando a base · {len(antes)} páginas antes\n")

    from ingestao import coletar, fragmentar, indexar  # importa aqui: carregar o modelo demora

    print("1/3 · Coletando páginas oficiais...")
    coletar.main()
    depois = fotografia()

    novas = sorted(set(depois) - set(antes))
    alteradas = sorted(u for u in set(antes) & set(depois) if antes[u] != depois[u])
    print(f"\n📋 Mudanças: {len(novas)} páginas novas · {len(alteradas)} alteradas · "
          f"{len(depois) - len(novas) - len(alteradas)} iguais")
    for u in novas:
        print("   + nova:     ", u)
    for u in alteradas:
        print("   ~ alterada: ", u)

    if not novas and not alteradas:
        print("\n✅ Nada mudou na documentação. O índice atual continua valendo.")
    else:
        print("\n2/3 · Fragmentando...")
        fragmentar.main()
        print("\n3/3 · Gerando embeddings e indexando...")
        indexar.main()
        print("\n✅ Base atualizada. Feche e abra o tutor e rode:  python avaliar.py")
    print(f"⏱️  {time.time() - inicio:.0f} s\n")


if __name__ == "__main__":
    main()
