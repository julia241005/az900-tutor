"""
ETAPA 3 da alimentação — EMBEDDINGS + INDEXAR
Cada fragmento vira um vetor (lista de números) que representa o SIGNIFICADO do texto.
Textos com sentido parecido ficam com vetores próximos — é isso que permite
buscar "por significado" e não só por palavra exata.
Os vetores são guardados num banco vetorial (ChromaDB), salvo em disco.

Rode:  python -m ingestao.indexar
(na 1ª vez baixa o modelo de embeddings, ~470 MB)
"""
import argparse
import json

import chromadb
from sentence_transformers import SentenceTransformer

import config
import trilhas
from config import MODELO_EMBEDDING


def carregar_fragmentos(arq_fragmentos) -> list[dict]:
    with arq_fragmentos.open(encoding="utf-8") as f:
        return [json.loads(linha) for linha in f]


def main(trilha_id: str = None):
    trilha_id = trilha_id or config.TRILHA_PADRAO
    nome_colecao = trilhas.obter(trilha_id).colecao
    pasta_vetores = config.pasta_vetores(trilha_id)
    fragmentos = carregar_fragmentos(config.arq_fragmentos(trilha_id))
    print(f"📄 {len(fragmentos)} fragmentos carregados (trilha: {trilha_id})")

    print(f"🧠 Carregando modelo de embeddings: {MODELO_EMBEDDING}")
    modelo = SentenceTransformer(MODELO_EMBEDDING)

    textos = [f["texto"] for f in fragmentos]
    vetores = modelo.encode(textos, show_progress_bar=True, normalize_embeddings=True)
    print(f"   Cada fragmento virou um vetor de {vetores.shape[1]} números")

    cliente = chromadb.PersistentClient(path=str(pasta_vetores))
    # recria a coleção do zero para não duplicar dados
    try:
        cliente.delete_collection(nome_colecao)
    except Exception:
        pass
    colecao = cliente.create_collection(nome_colecao, metadata={"hnsw:space": "cosine"})

    colecao.add(
        ids=[f["id"] for f in fragmentos],
        documents=textos,
        embeddings=vetores.tolist(),
        metadatas=[{k: f[k] for k in ("url", "titulo", "secao", "area", "tipo", "coletado_em")} for f in fragmentos],
    )
    print(f"✅ {colecao.count()} fragmentos indexados em {pasta_vetores}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Indexa (embeddings) os fragmentos de uma trilha no ChromaDB.")
    ap.add_argument("--trilha", default=None, help="id da trilha (padrão: trilha ativa).")
    main(ap.parse_args().trilha)
