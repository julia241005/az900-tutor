"""
buscar.py — Testa a RECUPERAÇÃO (o "R" do RAG), ainda sem LLM.
Mostra quais pedaços da documentação o tutor usaria para responder.

Rode:  python buscar.py "qual a diferença entre LRS e GRS?"
"""
import sys

import chromadb
from sentence_transformers import SentenceTransformer

from config import MODELO_EMBEDDING, NOME_COLECAO, PASTA_VETORES, TOP_K

_modelo = None
_colecao = None


def buscar(pergunta: str, k: int = TOP_K, area: str | None = None) -> list[dict]:
    """Retorna os k fragmentos mais parecidos com a pergunta."""
    global _modelo, _colecao
    if _modelo is None:
        _modelo = SentenceTransformer(MODELO_EMBEDDING)
        _colecao = chromadb.PersistentClient(path=str(PASTA_VETORES)).get_collection(NOME_COLECAO)

    vetor = _modelo.encode([pergunta], normalize_embeddings=True).tolist()
    filtro = {"area": area} if area else None
    r = _colecao.query(query_embeddings=vetor, n_results=k, where=filtro)

    return [
        {"texto": doc, "similaridade": round(1 - dist, 3), **meta}
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "O que é uma zona de disponibilidade?"
    print(f"\n🔎 Pergunta: {pergunta}\n")
    for i, res in enumerate(buscar(pergunta), 1):
        print(f"[{i}] similaridade {res['similaridade']}  |  {res['area']}")
        print(f"    {res['titulo']} › {res['secao']}")
        print(f"    {res['url']}")
        print(f"    {res['texto'][:250].replace(chr(10), ' ')}...\n")
