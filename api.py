"""
api.py — FASE 2: API do AZ-900 Tutor (FastAPI)

É a "porta de entrada" que o visual (Fase 5) vai usar para conversar com o tutor.

Rode:  uvicorn api:app --reload
Teste: abra http://localhost:8000/docs no navegador
"""
import json
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from openai import APIConnectionError
from pydantic import BaseModel, Field

import banco
import progresso
import seguranca
from agente import ResultadoAgente, conversar, conversar_stream
from config import LLM_MODELO, MODO_BUSCA, MODO_DEMO, ROTEAMENTO
from observabilidade import registrar
from rag import Resultado, cliente, responder, responder_stream
from sessao import nova_conversa

app = FastAPI(
    title="AZ-900 Tutor API",
    description="Tutor de IA para o exame AZ-900, com respostas baseadas na documentação oficial da Microsoft.",
    version="0.6.0",
)

# Permite que o frontend (Next.js, na porta 3000) chame esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


ERRO_IA = "Modelo de IA indisponível. Verifique se o Ollama está aberto."
ROTAS_COM_LIMITE = {"/chat", "/chat/stream", "/perguntar", "/perguntar/stream"}
limitador = seguranca.LimitadorDeTaxa()


@app.middleware("http")
async def protecao(request: Request, chamar_proxima):
    """Senha (se TUTOR_SENHA estiver definida) e limite de mensagens por minuto."""
    if request.url.path != "/saude" and not seguranca.senha_ok(request.headers.get("authorization")):
        return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="AZ-900 Tutor"'})
    if request.method == "POST" and request.url.path in ROTAS_COM_LIMITE:
        # Atrás de um proxy (ex.: Hugging Face), o IP real do visitante vem no cabeçalho X-Forwarded-For
        encaminhado = request.headers.get("x-forwarded-for", "")
        ip = encaminhado.split(",")[0].strip() or (request.client.host if request.client else "desconhecido")
        if not limitador.permitir(ip):
            registrar("api", rota=request.url.path, erro="limite_de_mensagens")
            return JSONResponse(status_code=429, headers={"Retry-After": "60"},
                                content={"erro": "Muitas mensagens em pouco tempo. Espere um minuto e tente de novo."})
    return await chamar_proxima(request)


@app.exception_handler(APIConnectionError)
def llm_fora_do_ar(request, _erro):
    """Se o Ollama estiver fechado, devolve um erro claro em vez de uma falha genérica."""
    registrar("api", rota=request.url.path, erro="ia_indisponivel")
    return JSONResponse(status_code=503, content={"erro": ERRO_IA})


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


def _ia_disponivel() -> bool:
    """Pergunta ao provedor do LLM (Ollama) se ele está respondendo. Espera no máximo 2 segundos."""
    try:
        cliente.with_options(timeout=2, max_retries=0).models.list()
        return True
    except Exception:
        return False


@app.get("/saude", tags=["Status"])
def saude():
    """Verifica se a API está no ar e se o modelo de IA (Ollama) está respondendo."""
    return {"status": "ok", "modelo": LLM_MODELO, "ia_disponivel": _ia_disponivel(), "modo_busca": MODO_BUSCA,
            "roteamento": ROTEAMENTO, "modo_demo": MODO_DEMO}


@app.post("/perguntar", tags=["Tutor"])
def perguntar(dados: Pergunta):
    """Responde a pergunta de uma vez (espera a resposta completa)."""
    r = responder(dados.pergunta)
    registrar("rag", pergunta=dados.pergunta, tipo="resposta", fontes=len(r.fontes), tokens_entrada=r.tokens_entrada,
              tokens_saida=r.tokens_saida, segundos=r.segundos, modelo=r.modelo)
    return asdict(r)


@app.post("/perguntar/stream", tags=["Tutor"])
def perguntar_stream(dados: Pergunta):
    """Responde em streaming (Server-Sent Events): o texto chega aos poucos.
    Eventos: {"evento": "texto", ...} durante a resposta e {"evento": "fim", ...} com fontes e métricas."""

    def eventos():
        try:
            for parte in responder_stream(dados.pergunta):
                if isinstance(parte, Resultado):
                    registrar("rag", pergunta=dados.pergunta, tipo="resposta", fontes=len(parte.fontes),
                              tokens_entrada=parte.tokens_entrada, tokens_saida=parte.tokens_saida,
                              segundos=parte.segundos, modelo=parte.modelo)
                    yield _sse({"evento": "fim", **asdict(parte)})
                else:
                    yield _sse({"evento": "texto", "conteudo": parte})
        except APIConnectionError:
            registrar("rag", pergunta=dados.pergunta, erro="ia_indisponivel")
            yield _sse({"evento": "erro", "erro": ERRO_IA})

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
        try:
            for parte in conversar_stream(dados.sessao_id, dados.mensagem):
                if isinstance(parte, ResultadoAgente):
                    yield _sse({"evento": "fim", **asdict(parte)})
                else:
                    yield _sse({"evento": "texto", "conteudo": parte})
        except APIConnectionError:  # no streaming o erro acontece depois do início da resposta
            registrar("agente", sessao=dados.sessao_id, pergunta=dados.mensagem, erro="ia_indisponivel")
            yield _sse({"evento": "erro", "erro": ERRO_IA})

    return StreamingResponse(eventos(), media_type="text/event-stream")


@app.get("/chat/historico/{sessao_id}", tags=["Agente"])
def chat_historico(sessao_id: str, limite: int = Query(50, ge=1, le=200)):
    """Mensagens salvas da conversa (para a interface mostrar a conversa ao reabrir)."""
    return banco.mensagens_da_sessao(sessao_id, limite)


@app.delete("/chat/historico/{sessao_id}", tags=["Agente"])
def chat_nova_conversa(sessao_id: str):
    """Começa uma conversa nova (apaga o histórico do chat; o progresso continua)."""
    nova_conversa(sessao_id)
    return {"ok": True}
