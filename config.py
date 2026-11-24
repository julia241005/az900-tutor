"""
config.py — Configurações centrais do projeto.
Tudo que pode mudar fica aqui, num lugar só.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

import trilhas

load_dotenv()  # lê o arquivo .env, se existir (opcional neste projeto)

# ── Trilha ativa ──────────────────────────────────────────────────────────
# Cada certificação ("trilha") guarda seus dados numa pasta própria: data/<id>/...
# Assim o progresso, os vetores e o banco de uma certificação não se misturam
# com os de outra. A trilha padrão (ao rodar scripts no terminal) vem do .env
# (TRILHA=...) ou é o AZ-900. Na interface web, o usuário escolhe a trilha e ela
# é passada em cada requisição.
TRILHA_PADRAO = os.getenv("TRILHA", trilhas.TRILHA_PADRAO)
if not trilhas.existe(TRILHA_PADRAO):
    TRILHA_PADRAO = trilhas.TRILHA_PADRAO

# ── Pastas (por trilha) ───────────────────────────────────────────────────
RAIZ = Path(__file__).parent


def dir_trilha(trilha_id: str | None = None) -> Path:
    return RAIZ / "data" / (trilha_id or TRILHA_PADRAO)


def pasta_brutos(trilha_id: str | None = None) -> Path:
    return dir_trilha(trilha_id) / "brutos"              # textos baixados (1 arquivo por página)


def arq_fragmentos(trilha_id: str | None = None) -> Path:
    return dir_trilha(trilha_id) / "fragmentos.jsonl"    # pedaços prontos para indexar


def pasta_vetores(trilha_id: str | None = None) -> Path:
    return dir_trilha(trilha_id) / "vetores"             # banco vetorial (ChromaDB)


def arq_banco(trilha_id: str | None = None) -> Path:
    return dir_trilha(trilha_id) / "tutor.db"            # banco SQLite: respostas, perguntas e histórico

def arq_log(trilha_id: str | None = None) -> Path:
    return dir_trilha(trilha_id) / "logs" / "interacoes.jsonl"  # log de interações (observabilidade)


def colecao(trilha_id: str | None = None) -> str:
    return trilhas.obter(trilha_id or TRILHA_PADRAO).colecao


# Constantes da trilha padrão (mantidas para os scripts e testes que não passam trilha)
PASTA_BRUTOS = pasta_brutos()
ARQ_FRAGMENTOS = arq_fragmentos()
PASTA_VETORES = pasta_vetores()
ARQ_BANCO = arq_banco()
ARQ_LOG = arq_log()

# ── Fragmentação (chunking) ──────────────────────────────────────────────
TAMANHO_FRAGMENTO = 1200   # caracteres por pedaço (~300 tokens)
SOBREPOSICAO = 200         # caracteres repetidos entre pedaços vizinhos

# ── Embeddings — modelo gratuito, roda no seu computador, entende português
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ── Busca (Retrieval) ────────────────────────────────────────────────────
NOME_COLECAO = colecao()  # coleção de vetores da trilha padrão
TOP_K = int(os.getenv("TOP_K", "4"))  # quantos pedaços buscar para cada pergunta
SIMILARIDADE_MINIMA = 0.30    # abaixo disso, o trecho é considerado irrelevante (exceto se tiver palavra exata em comum)
MODO_BUSCA = os.getenv("MODO_BUSCA", "hibrida")  # "hibrida" (significado + palavra exata) ou "vetorial"

# ── LLM (o "cérebro") ────────────────────────────────────────────────────
# Padrão: Ollama local (gratuito). A API é compatível com o formato OpenAI,
# então trocar de provedor é só mudar estas 3 variáveis (no .env, se quiser).
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/v1")
LLM_MODELO = os.getenv("LLM_MODELO", "qwen2.5:3b")
LLM_CHAVE = os.getenv("LLM_CHAVE", "ollama")  # o Ollama não exige chave; o texto é só um marcador
LLM_TEMPERATURA = 0.2   # baixa = respostas mais fiéis e menos "criativas"
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "700"))  # limite de tamanho da resposta

# ── Agente ───────────────────────────────────────────────────────────────
# "regras": o código decide (dúvida, simulado, progresso) e o LLM é chamado 1 vez → mais rápido.
# "llm":    o LLM decide qual ferramenta usar (tool calling) → 2 chamadas por pergunta, mais lento.
ROTEAMENTO = os.getenv("ROTEAMENTO", "regras")

# ── Publicação ───────────────────────────────────────────────────────────
# MODO_DEMO=1 na versão online: cada navegador tem a própria sessão e a interface mostra um aviso.
MODO_DEMO = os.getenv("MODO_DEMO", "0") == "1"

# ── Simulado ─────────────────────────────────────────────────────────────
# Na avaliação, o modelo local (3B) gerou 11 perguntas e nenhuma foi aprovada na revisão
# humana. Por isso o simulado usa só perguntas APROVADAS. Mude para True apenas para
# experimentos (perguntas geradas na hora aparecem com o selo "nova (em revisão)").
SIMULADO_GERAR_COM_IA = False

# ── FinOps: preço de REFERÊNCIA para estimar quanto custaria numa API paga ──
# Valores HIPOTÉTICOS em US$ por 1 milhão de tokens. Ajuste com o preço atual do provedor que quiser comparar.
PRECO_REF_ENTRADA_1M = float(os.getenv("PRECO_REF_ENTRADA_1M", "0.15"))
PRECO_REF_SAIDA_1M = float(os.getenv("PRECO_REF_SAIDA_1M", "0.60"))

# ── Segurança (para quando o tutor for publicado) ─────────────────────────
TUTOR_SENHA = os.getenv("TUTOR_SENHA", "")          # vazio = sem senha (uso só no seu computador)
LIMITE_MENSAGENS_POR_MINUTO = int(os.getenv("LIMITE_MENSAGENS_POR_MINUTO", "20"))
