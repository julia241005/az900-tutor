"""
conftest.py — preparação comum dos testes.

Cada teste usa um banco SQLite e um arquivo de log TEMPORÁRIOS: os testes nunca
mexem no seu progresso real (data/tutor.db) nem no log real.
Os testes não precisam do Ollama nem do índice: rodam em poucos segundos.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # permite "import banco" etc.


@pytest.fixture(autouse=True)
def arquivos_temporarios(tmp_path, monkeypatch):
    import banco
    import observabilidade
    import sessao
    monkeypatch.setattr(banco, "ARQ_BANCO", tmp_path / "teste.db")
    monkeypatch.setattr(observabilidade, "ARQ_LOG", tmp_path / "logs" / "interacoes.jsonl")
    sessao._SESSOES.clear()
    yield
    sessao._SESSOES.clear()


@pytest.fixture
def pergunta_exemplo():
    return {
        "area": "Gestão e governança do Azure",
        "enunciado": "Qual serviço garante que os recursos sigam regras da empresa?",
        "alternativas": {"A": "Azure Policy", "B": "Azure Advisor", "C": "Azure Monitor", "D": "Azure Arc"},
        "correta": "A",
        "explicacao": "O Azure Policy avalia os recursos e aplica regras de conformidade.",
        "fonte": {"titulo": "Azure Policy", "url": "https://learn.microsoft.com/pt-br/azure/governance/policy/overview"},
    }
