"""
buscar.py — RECUPERAÇÃO (o "R" do RAG).

Dois modos (escolha em config.MODO_BUSCA):
  - "vetorial": só por significado (embeddings no ChromaDB)
  - "hibrida" : significado + palavra exata (BM25), combinados por RRF.
                Ajuda muito com siglas curtas como LRS, GRS, ZRS e nomes de serviços.

Detalhes e resultados da comparação: docs/04-embeddings-e-indexacao.md e docs/09-avaliacao.md

Rode:  python buscar.py "qual a diferença entre LRS e GRS?"
"""
import math
import random
import re
import sys
import unicodedata
from collections import Counter

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from config import MODELO_EMBEDDING, MODO_BUSCA, NOME_COLECAO, PASTA_VETORES, TOP_K

_modelo = None
_colecao = None
_indice = None  # cache: fragmentos + vetores + índice de palavras, carregado uma vez

# Unidades de introdução e resumo falam do curso (ex.: como usar o Copilot), não do conteúdo da prova
UNIDADES_SEM_CONTEUDO_DE_PROVA = ("/1-introduction", "-summary")

PALAVRAS_VAZIAS = set("""a o as os um uma uns umas de do da dos das em no na nos nas por para com sem e ou que
qual quais como quando onde porque se ao aos à às é são ser foi entre sobre mais menos muito muita seu sua seus suas
the of to and in is for on with it this that be are or as by an at from""".split())


# ── Texto → palavras ─────────────────────────────────────────────────────────
def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def tokenizar(texto: str) -> list[str]:
    palavras = re.findall(r"[a-z0-9]+", _sem_acento(texto.lower()))
    return [p for p in palavras if len(p) > 1 and p not in PALAVRAS_VAZIAS]


def siglas(texto: str) -> set[str]:
    """Siglas digitadas em maiúsculas (LRS, GRS, RBAC, VPN...) recebem peso extra na busca por palavra."""
    return {s.lower() for s in re.findall(r"\b[A-Z][A-Z0-9-]{1,7}\b", texto)}


# ── Busca por palavra exata: BM25 ────────────────────────────────────────────
class BM25:
    """Algoritmo clássico de busca por palavras (o mesmo princípio de buscadores tradicionais)."""

    def __init__(self, documentos: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(d) for d in documentos]
        self.tamanhos = [len(d) for d in documentos]
        self.media = (sum(self.tamanhos) / len(self.tamanhos)) if documentos else 0
        n = len(documentos)
        df = Counter(p for d in self.docs for p in d)
        self.idf = {p: math.log(1 + (n - f + 0.5) / (f + 0.5)) for p, f in df.items()}

    def pontuar(self, consulta: list[str], pesos: dict[str, float] | None = None) -> np.ndarray:
        pesos = pesos or {}
        notas = np.zeros(len(self.docs))
        for i, (d, tam) in enumerate(zip(self.docs, self.tamanhos)):
            s = 0.0
            for p in consulta:
                f = d.get(p, 0)
                if f:
                    s += pesos.get(p, 1.0) * self.idf.get(p, 0) * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * tam / (self.media or 1)))
            notas[i] = s
        return notas


def fusao_rrf(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    """Reciprocal Rank Fusion: junta listas ordenadas dando pontos pela posição (1/(k+posição))."""
    notas: dict[int, float] = {}
    for ranking in rankings:
        for pos, i in enumerate(ranking):
            notas[i] = notas.get(i, 0.0) + 1.0 / (k + pos + 1)
    return notas


# ── Carregamento ─────────────────────────────────────────────────────────────
def _colecao_chroma():
    global _colecao
    if _colecao is None:
        _colecao = chromadb.PersistentClient(path=str(PASTA_VETORES)).get_collection(NOME_COLECAO)
    return _colecao


def _modelo_embedding():
    global _modelo
    if _modelo is None:
        _modelo = SentenceTransformer(MODELO_EMBEDDING)
    return _modelo


def _carregar_indice():
    """Lê todos os fragmentos uma vez e monta o índice de palavras (BM25) em memória."""
    global _indice
    if _indice is None:
        r = _colecao_chroma().get(include=["documents", "metadatas", "embeddings"])
        vetores = np.array(r["embeddings"], dtype=np.float32)
        textos_busca = [f"{m.get('titulo', '')} {m.get('secao', '')} {d}" for d, m in zip(r["documents"], r["metadatas"])]
        _indice = {
            "docs": r["documents"], "metas": r["metadatas"], "vetores": vetores,
            "bm25": BM25([tokenizar(t) for t in textos_busca]),
        }
    return _indice


def amostra_por_area(area: str | None, n: int) -> list[dict]:
    """Sorteia n trechos de conteúdo (sem o guia de estudo) de uma área do exame."""
    idx = _carregar_indice()
    candidatos = [
        {"texto": doc, "similaridade": 1.0, **meta}
        for doc, meta in zip(idx["docs"], idx["metas"])
        if meta.get("tipo") != "guia" and len(doc) > 300 and (not area or meta.get("area") == area)
        and not any(p in meta.get("url", "") for p in UNIDADES_SEM_CONTEUDO_DE_PROVA)
    ]
    return random.sample(candidatos, min(n, len(candidatos)))


# ── Busca ────────────────────────────────────────────────────────────────────
def buscar(pergunta: str, k: int = TOP_K, area: str | None = None, modo: str | None = None) -> list[dict]:
    """Retorna os k fragmentos mais relevantes para a pergunta.
    Cada resultado traz 'similaridade' (significado, 0 a 1) e 'palavra_chave' (se houve palavra exata em comum)."""
    modo = modo or MODO_BUSCA
    idx = _carregar_indice()
    consulta = _modelo_embedding().encode([pergunta], normalize_embeddings=True)[0]
    sims = idx["vetores"] @ consulta  # similaridade de cosseno (vetores normalizados)

    candidatos = [i for i, m in enumerate(idx["metas"]) if not area or m.get("area") == area]
    if not candidatos:
        return []
    ordem_vetorial = sorted(candidatos, key=lambda i: -sims[i])

    termos = tokenizar(pergunta)
    notas_bm25 = idx["bm25"].pontuar(termos, {s: 3.0 for s in siglas(pergunta)})

    if modo == "vetorial":
        escolhidos = ordem_vetorial[:k]
    else:
        ordem_palavras = [i for i in sorted(candidatos, key=lambda i: -notas_bm25[i]) if notas_bm25[i] > 0]
        notas = fusao_rrf([ordem_vetorial[:20], ordem_palavras[:20]])
        escolhidos = sorted(notas, key=lambda i: -notas[i])[:k]

    return [
        {"texto": idx["docs"][i], "similaridade": round(float(sims[i]), 3),
         "palavra_chave": bool(notas_bm25[i] > 0), **idx["metas"][i]}
        for i in escolhidos
    ]


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "O que é uma zona de disponibilidade?"
    print(f"\n🔎 Pergunta: {pergunta}   (modo: {MODO_BUSCA})\n")
    for i, res in enumerate(buscar(pergunta), 1):
        marca = " · palavra exata" if res["palavra_chave"] else ""
        print(f"[{i}] similaridade {res['similaridade']}{marca}  |  {res['area']}")
        print(f"    {res['titulo']} › {res['secao']}")
        print(f"    {res['url']}")
        print(f"    {res['texto'][:250].replace(chr(10), ' ')}...\n")
