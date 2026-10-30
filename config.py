"""
config.py — Configurações centrais do projeto.
Tudo que pode mudar fica aqui, num lugar só.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env, se existir (opcional neste projeto)

# ── Pastas ────────────────────────────────────────────────────────────────
RAIZ = Path(__file__).parent
PASTA_BRUTOS = RAIZ / "data" / "brutos"              # textos baixados (1 arquivo por página)
ARQ_FRAGMENTOS = RAIZ / "data" / "fragmentos.jsonl"  # pedaços prontos para indexar
PASTA_VETORES = RAIZ / "data" / "vetores"            # banco vetorial (ChromaDB)

# ── Fragmentação (chunking) ──────────────────────────────────────────────
TAMANHO_FRAGMENTO = 1200   # caracteres por pedaço (~300 tokens)
SOBREPOSICAO = 200         # caracteres repetidos entre pedaços vizinhos

# ── Embeddings — modelo gratuito, roda no seu computador, entende português
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ── Busca (Retrieval) ────────────────────────────────────────────────────
NOME_COLECAO = "az900"
TOP_K = 4                     # quantos pedaços buscar para cada pergunta
SIMILARIDADE_MINIMA = 0.30    # abaixo disso, o trecho é considerado irrelevante

# ── LLM (o "cérebro") ────────────────────────────────────────────────────
# Padrão: Ollama local (gratuito). A API é compatível com o formato OpenAI,
# então trocar de provedor é só mudar estas 3 variáveis (no .env, se quiser).
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/v1")
LLM_MODELO = os.getenv("LLM_MODELO", "qwen2.5:3b")
LLM_CHAVE = os.getenv("LLM_CHAVE", "ollama")  # o Ollama não exige chave; o texto é só um marcador
LLM_TEMPERATURA = 0.2   # baixa = respostas mais fiéis e menos "criativas"
LLM_MAX_TOKENS = 700    # limite de tamanho da resposta
