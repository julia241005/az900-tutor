"""
banco.py — Banco de dados (SQLite) do tutor: MEMÓRIA DE LONGO PRAZO.

Tabelas:
  respostas  → cada resposta do aluno no simulado (base do painel de progresso)
  perguntas  → banco de perguntas, com status de revisão humana:
               pendente → aprovada / rejeitada   (human-in-the-loop)

O arquivo fica em data/tutor.db (fora do Git). SQLite já vem com o Python: nada a instalar.
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import ARQ_BANCO

ESQUEMA = """
CREATE TABLE IF NOT EXISTS respostas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id   TEXT NOT NULL,
    area        TEXT NOT NULL,
    enunciado   TEXT NOT NULL,
    correta     INTEGER NOT NULL,          -- 1 = acertou, 0 = errou
    fonte_titulo TEXT,
    fonte_url   TEXT,
    respondida_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS perguntas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    area        TEXT NOT NULL,
    enunciado   TEXT NOT NULL UNIQUE,
    alternativas TEXT NOT NULL,            -- JSON {"A": "...", ...}
    correta     TEXT NOT NULL,
    explicacao  TEXT,
    fonte_titulo TEXT,
    fonte_url   TEXT,
    status      TEXT NOT NULL DEFAULT 'pendente',   -- pendente | aprovada | rejeitada
    criada_em   TEXT NOT NULL
);
"""


@contextmanager
def conectar():
    ARQ_BANCO.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ARQ_BANCO)
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Respostas do aluno ──────────────────────────────────────────────────────
def registrar_resposta(sessao_id: str, pergunta: dict, acertou: bool):
    with conectar() as con:
        con.execute(
            "INSERT INTO respostas (sessao_id, area, enunciado, correta, fonte_titulo, fonte_url, respondida_em) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sessao_id, pergunta["area"], pergunta["enunciado"], int(acertou),
             pergunta["fonte"]["titulo"], pergunta["fonte"]["url"], _agora()),
        )


def respostas_do_aluno(sessao_id: str) -> list[dict]:
    with conectar() as con:
        linhas = con.execute("SELECT * FROM respostas WHERE sessao_id = ? ORDER BY id", (sessao_id,))
        return [dict(l) for l in linhas]


# ── Banco de perguntas ──────────────────────────────────────────────────────
def _linha_para_pergunta(l: sqlite3.Row) -> dict:
    return {
        "id": l["id"], "area": l["area"], "enunciado": l["enunciado"],
        "alternativas": json.loads(l["alternativas"]), "correta": l["correta"],
        "explicacao": l["explicacao"], "status": l["status"],
        "fonte": {"titulo": l["fonte_titulo"], "url": l["fonte_url"]},
    }


def salvar_pergunta(p: dict, status: str = "pendente") -> int | None:
    """Salva uma pergunta gerada pela IA. Ignora duplicadas (mesmo enunciado)."""
    with conectar() as con:
        cur = con.execute(
            "INSERT OR IGNORE INTO perguntas (area, enunciado, alternativas, correta, explicacao, "
            "fonte_titulo, fonte_url, status, criada_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (p["area"], p["enunciado"], json.dumps(p["alternativas"], ensure_ascii=False), p["correta"],
             p["explicacao"], p["fonte"]["titulo"], p["fonte"]["url"], status, _agora()),
        )
        return cur.lastrowid if cur.rowcount else None


def perguntas_aprovadas(area: str | None, quantidade: int, evitar: set[str] = frozenset()) -> list[dict]:
    """Sorteia perguntas já aprovadas por humano, evitando as que o aluno já respondeu."""
    sql = "SELECT * FROM perguntas WHERE status = 'aprovada'"
    params: list = []
    if area:
        sql += " AND area = ?"
        params.append(area)
    sql += " ORDER BY RANDOM()"
    with conectar() as con:
        todas = [_linha_para_pergunta(l) for l in con.execute(sql, params)]
    novas = [p for p in todas if p["enunciado"] not in evitar]
    return (novas or todas)[:quantidade]


def perguntas_por_status(status: str = "pendente") -> list[dict]:
    with conectar() as con:
        return [_linha_para_pergunta(l) for l in con.execute("SELECT * FROM perguntas WHERE status = ? ORDER BY id", (status,))]


def definir_status(pergunta_id: int, status: str):
    with conectar() as con:
        con.execute("UPDATE perguntas SET status = ? WHERE id = ?", (status, pergunta_id))


def resumo_banco() -> dict:
    with conectar() as con:
        linhas = con.execute("SELECT area, status, COUNT(*) AS n FROM perguntas GROUP BY area, status")
        resumo: dict = {}
        for l in linhas:
            resumo.setdefault(l["area"], {})[l["status"]] = l["n"]
        return resumo
