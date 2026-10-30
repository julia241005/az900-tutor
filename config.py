"""
config.py — Configurações centrais do projeto.
Tudo que pode mudar fica aqui, num lugar só.
"""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env (chave da API etc.)

# Pastas
RAIZ = Path(__file__).parent
PASTA_BRUTOS = RAIZ / "data" / "brutos"          # textos baixados (1 arquivo por página)
ARQ_FRAGMENTOS = RAIZ / "data" / "fragmentos.jsonl"  # pedaços prontos para indexar
PASTA_VETORES = RAIZ / "data" / "vetores"         # banco vetorial (ChromaDB)

# Fragmentação (chunking)
TAMANHO_FRAGMENTO = 1200   # caracteres por pedaço (~300 tokens)
SOBREPOSICAO = 200         # caracteres repetidos entre pedaços vizinhos

# Embeddings — modelo gratuito, roda no seu computador, entende português
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Banco vetorial
NOME_COLECAO = "az900"
TOP_K = 4  # quantos pedaços buscar para cada pergunta
