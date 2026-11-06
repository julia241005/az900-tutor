"""Log de interações e relatório de custo (FinOps)."""
import observabilidade
import relatorio


def test_registrar_e_ler_eventos():
    observabilidade.registrar("agente", sessao="web", pergunta="x" * 500, tipo="resposta",
                              tokens_entrada=1000, tokens_saida=200, segundos=3.5)
    eventos = observabilidade.ler_eventos()
    assert len(eventos) == 1
    assert len(eventos[0]["pergunta"]) == 200          # pergunta guardada só em parte (privacidade)


def test_custo_de_referencia(monkeypatch):
    monkeypatch.setattr(observabilidade, "PRECO_REF_ENTRADA_1M", 1.0)
    monkeypatch.setattr(observabilidade, "PRECO_REF_SAIDA_1M", 2.0)
    assert observabilidade.custo_referencia(1_000_000, 500_000) == 2.0


def test_resumo_do_relatorio():
    eventos = [
        {"sessao": "a", "tipo": "resposta", "ferramentas": ["buscar_documentacao"], "fontes": 3,
         "tokens_entrada": 900, "tokens_saida": 100, "segundos": 4.0},
        {"sessao": "b", "tipo": "simulado", "ferramentas": ["gerar_simulado"], "segundos": 0.2},
        {"sessao": "a", "erro": "ia_indisponivel"},
    ]
    r = relatorio.resumir(eventos)
    assert r["interacoes"] == 3 and r["erros"] == 1 and r["alunos"] == 2
    assert r["tokens_entrada"] == 900
    assert r["por_tipo"]["simulado"] == 1


def test_percentil():
    assert relatorio.percentil(list(range(1, 101)), 95) == 95
    assert relatorio.percentil([], 95) == 0.0
