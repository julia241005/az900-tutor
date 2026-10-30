"""
ETAPA 3 da alimentação — EMBEDDINGS + INDEXAR
Cada fragmento vira um vetor (lista de números) que representa o SIGNIFICADO do texto.
Textos com sentido parecido ficam com vetores próximos — é isso que permite
buscar "por significado" e não só por palavra exata.
Os vetores são guardados num banco vetorial (ChromaDB), salvo em disco.

Rode:  python -m ingestao.indexar
(na 1ª vez baixa o modelo de embeddings, ~470 MB)
"""
import json

import chromadb
from sentence_transformers import SentenceTransformer

from config import ARQ_FRAGMENTOS, MODELO_EMBEDDING, NOME_COLECAO, PASTA_VETORES


def carregar_fragmentos() -> list[dict]:
    with ARQ_FRAGMENTOS.open(encoding="utf-8") as f:
        return [json.loads(linha) for linha in f]


def main():
    fragmentos = carregar_fragmentos()
    print(f"📄 {len(fragmentos)} fragmentos carregados")

    print(f"🧠 Carregando modelo de embeddings: {MODELO_EMBEDDING}")
    modelo = SentenceTransformer(MODELO_EMBEDDING)

    textos = [f["texto"] for f in fragmentos]
    vetores = modelo.encode(textos, show_progress_bar=True, normalize_embeddings=True)
    print(f"   Cada fragmento virou um vetor de {vetores.shape[1]} números")

    cliente = chromadb.PersistentClient(path=str(PASTA_VETORES))
    # recria a coleção do zero para não duplicar dados
    try:
        cliente.delete_collection(NOME_COLECAO)
    except Exception:
        pass
    colecao = cliente.create_collection(NOME_COLECAO, metadata={"hnsw:space": "cosine"})

    colecao.add(
        ids=[f["id"] for f in fragmentos],
        documents=textos,
        embeddings=vetores.tolist(),
        metadatas=[{k: f[k] for k in ("url", "titulo", "secao", "area", "tipo", "coletado_em")} for f in fragmentos],
    )
    print(f"✅ {colecao.count()} fragmentos indexados em data/vetores/")


if __name__ == "__main__":
    main()
