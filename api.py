"""
api.py — FASE 2: API do AZ-900 Tutor (FastAPI)

É a "porta de entrada" que o visual (Fase 5) vai usar para conversar com o tutor.

Rode:  uvicorn api:app --reload
Teste: abra http://localhost:8000/docs no navegador
"""
import json
from dataclasses import asdict

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from openai import APIConnectionError
from pydantic import BaseModel, Field

import banco
import progresso
from agente import ResultadoAgente, conversar, conversar_stream
from config import LLM_MODELO
from rag import Resultado, responder, responder_stream

app = FastAPI(
    title="AZ-900 Tutor API",
    description="Tutor de IA para o exame AZ-900, com respostas baseadas na documentação oficial da Microsoft.",
    version="0.5.0",
)

# Permite que o frontend (Next.js, na porta 3000) chame esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIConnectionError)
def llm_fora_do_ar(_request, _erro):
    """Se o Ollama estiver fechado, devolve um erro claro em vez de uma falha genérica."""
    return JSONResponse(status_code=503, content={"erro": "Modelo de IA indisponível. Verifique se o Ollama está aberto."})


class Pergunta(BaseModel):
    pergunta: str = Field(..., min_length=3, max_length=500,
                          examples=["Qual a diferença entre LRS e GRS?"])


class Mensagem(BaseModel):
    sessao_id: str = Field(..., min_length=1, max_length=64, examples=["aluno-1"])
    mensagem: str = Field(..., min_length=1, max_length=500,
                          examples=["Me faz um simulado de governança com 2 perguntas"])


def _sse(dados: dict) -> str:
    return f"data: {json.dumps(dados, ensure_ascii=False)}\n\n"


PAGINA = Path(__file__).parent / "web" / "index.html"


@app.get("/", include_in_schema=False)
def interface():
    """Interface gráfica do tutor (chat, simulado e progresso)."""
    return FileResponse(PAGINA)


class Resposta(BaseModel):
    sessao_id: str = Field(..., min_length=1, max_length=64)
    pergunta_id: int
    resposta: str = Field(..., pattern="^[ABCD]$")


@app.get("/simulado/perguntas", tags=["Simulado"])
def simulado_perguntas(sessao_id: str, area: str | None = None, quantidade: int = Query(5, ge=1, le=30)):
    """Sorteia perguntas APROVADAS do banco (sem gabarito), evitando as que o aluno já respondeu.
    Não usa IA: é instantâneo."""
    ja = {r["enunciado"] for r in banco.respostas_do_aluno(sessao_id)}
    perguntas = banco.perguntas_aprovadas(area or None, quantidade, evitar=ja)
    return [{k: p[k] for k in ("id", "area", "enunciado", "alternativas")} for p in perguntas]


@app.post("/simulado/responder", tags=["Simulado"])
def simulado_responder(dados: Resposta):
    """Corrige por código (sem IA), registra no progresso e devolve a explicação com a fonte."""
    p = banco.obter_pergunta(dados.pergunta_id)
    if not p:
        raise HTTPException(404, "Pergunta não encontrada")
    acertou = dados.resposta == p["correta"]
    banco.registrar_resposta(dados.sessao_id, p, acertou)
    return {"acertou": acertou, "correta": p["correta"], "explicacao": p["explicacao"], "fonte": p["fonte"]}


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


@app.get("/progresso/{sessao_id}", tags=["Progresso"])
def ver_progresso(sessao_id: str):
    """Desempenho do aluno por área do exame (com pesos oficiais) e recomendação de estudo."""
    return progresso.calcular(sessao_id)


@app.get("/banco/resumo", tags=["Progresso"])
def resumo_banco():
    """Quantidade de perguntas no banco por área e status (pendente, aprovada, rejeitada)."""
    return banco.resumo_banco()


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
