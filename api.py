"""
api.py — FASE 2: API do AZ-900 Tutor (FastAPI)

É a "porta de entrada" que o visual (Fase 5) vai usar para conversar com o tutor.

Rode:  uvicorn api:app --reload
Teste: abra http://localhost:8000/docs no navegador
"""
import json
from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agente import ResultadoAgente, conversar, conversar_stream
from config import LLM_MODELO
from rag import Resultado, responder, responder_stream

app = FastAPI(
    title="AZ-900 Tutor API",
    description="Tutor de IA para o exame AZ-900, com respostas baseadas na documentação oficial da Microsoft.",
    version="0.3.0",
)

# Permite que o frontend (Next.js, na porta 3000) chame esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pergunta(BaseModel):
    pergunta: str = Field(..., min_length=3, max_length=500,
                          examples=["Qual a diferença entre LRS e GRS?"])


class Mensagem(BaseModel):
    sessao_id: str = Field(..., min_length=1, max_length=64, examples=["aluno-1"])
    mensagem: str = Field(..., min_length=1, max_length=500,
                          examples=["Me faz um simulado de governança com 2 perguntas"])


def _sse(dados: dict) -> str:
    return f"data: {json.dumps(dados, ensure_ascii=False)}\n\n"


@app.get("/saude", tags=["Status"])
def saude():
    """Verifica se a API está no ar."""
    return {"status": "ok", "modelo": LLM_MODELO}


@app.post("/perguntar", tags=["Tutor"])
def perguntar(dados: Pergunta):
    """Responde a pergunta de uma vez (espera a resposta completa)."""
    return asdict(responder(dados.pergunta))


@app.post("/perguntar/stream", tags=["Tutor"])
def perguntar_stream(dados: Pergunta):
    """Responde em streaming (Server-Sent Events): o texto chega aos poucos.
    Eventos: {"evento": "texto", ...} durante a resposta e {"evento": "fim", ...} com fontes e métricas."""

    def eventos():
        for parte in responder_stream(dados.pergunta):
            if isinstance(parte, Resultado):
                dados_fim = {"evento": "fim", **asdict(parte)}
                yield f"data: {json.dumps(dados_fim, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'evento': 'texto', 'conteudo': parte}, ensure_ascii=False)}\n\n"

    return StreamingResponse(eventos(), media_type="text/event-stream")


@app.post("/chat", tags=["Agente"])
def chat(dados: Mensagem):
    """Conversa com o agente (com memória por sessão). Ele decide se busca na documentação,
    gera um simulado ou corrige uma resposta (envie só a letra: A, B, C ou D)."""
    return asdict(conversar(dados.sessao_id, dados.mensagem))


@app.post("/chat/stream", tags=["Agente"])
def chat_stream(dados: Mensagem):
    """Mesmo que /chat, em streaming (Server-Sent Events)."""

    def eventos():
        for parte in conversar_stream(dados.sessao_id, dados.mensagem):
            if isinstance(parte, ResultadoAgente):
                yield _sse({"evento": "fim", **asdict(parte)})
            else:
                yield _sse({"evento": "texto", "conteudo": parte})

    return StreamingResponse(eventos(), media_type="text/event-stream")
