"""API: status, senha, limite de mensagens, histórico e erro claro sem o Ollama.
O LLM é substituído por funções falsas: não precisa do Ollama aberto."""
import base64

import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError

import api
import seguranca


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setattr(seguranca, "SENHA", "")
    monkeypatch.setattr(api, "limitador", seguranca.LimitadorDeTaxa(limite=100))
    monkeypatch.setattr(api, "_ia_disponivel", lambda: True)
    return TestClient(api.app)


def test_saude(cliente):
    d = cliente.get("/saude").json()
    assert d["status"] == "ok" and d["ia_disponivel"] is True


def test_senha_protege_a_interface(cliente, monkeypatch):
    monkeypatch.setattr(seguranca, "SENHA", "estudar900")
    assert cliente.get("/banco/resumo").status_code == 401
    assert cliente.get("/saude").status_code == 200          # status continua aberto (monitoramento)
    ok = "Basic " + base64.b64encode(b"julia:estudar900").decode()
    assert cliente.get("/banco/resumo", headers={"Authorization": ok}).status_code == 200


def test_limite_de_mensagens(cliente, monkeypatch):
    monkeypatch.setattr(api, "limitador", seguranca.LimitadorDeTaxa(limite=2))
    monkeypatch.setattr(api, "conversar_stream", lambda s, m: iter(["oi"]))
    codigos = [cliente.post("/chat/stream", json={"sessao_id": "t", "mensagem": "oi"}).status_code for _ in range(3)]
    assert codigos == [200, 200, 429]


def test_stream_avisa_quando_a_ia_esta_fora(cliente, monkeypatch):
    def quebra(_s, _m):
        raise APIConnectionError(request=None)
        yield  # noqa: faz desta função um gerador
    monkeypatch.setattr(api, "conversar_stream", quebra)
    corpo = cliente.post("/chat/stream", json={"sessao_id": "t", "mensagem": "oi"}).text
    assert '"evento": "erro"' in corpo and "Ollama" in corpo


def test_historico_e_nova_conversa(cliente):
    import sessao
    sessao.obter_sessao("web").lembrar("user", "O que é ZRS?")
    assert cliente.get("/chat/historico/web").json()[0]["texto"] == "O que é ZRS?"
    cliente.delete("/chat/historico/web")
    assert cliente.get("/chat/historico/web").json() == []


def test_simulado_sem_ia(cliente, pergunta_exemplo):
    import banco
    banco.salvar_pergunta(pergunta_exemplo, status="aprovada")
    q = cliente.get("/simulado/perguntas", params={"sessao_id": "t", "quantidade": 1}).json()[0]
    assert "correta" not in q                                  # gabarito nunca vai para o navegador
    r = cliente.post("/simulado/responder", json={"sessao_id": "t", "pergunta_id": q["id"], "resposta": "A"}).json()
    assert r["acertou"] is True
