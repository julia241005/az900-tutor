"""
banco.py — Banco de dados (SQLite) do tutor: MEMÓRIA DE LONGO PRAZO.

Tabelas:
  respostas  → cada resposta do aluno no simulado (base do painel de progresso)
  perguntas  → banco de perguntas, com status de revisão humana:
               pendente → aprovada / rejeitada   (human-in-the-loop)
  mensagens  → histórico do chat (a conversa continua mesmo depois de fechar o tutor)

O arquivo fica em data/tutor.db (fora do Git). SQLite já vem com o Python: nada a instalar.
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import config
from config import ARQ_BANCO, TRILHA_PADRAO

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
CREATE TABLE IF NOT EXISTS mensagens (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id   TEXT NOT NULL,
    papel       TEXT NOT NULL,             -- user | assistant
    texto       TEXT NOT NULL,
    extra       TEXT,                      -- JSON: fontes, tipo (para redesenhar o chat)
    criada_em   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mensagens_sessao ON mensagens (sessao_id, id);
"""


def _caminho(trilha: str | None) -> "object":
    """Caminho do banco da trilha. Para a trilha padrão usa ARQ_BANCO (módulo),
    que os testes substituem por um arquivo temporário (monkeypatch)."""
    if trilha is None or trilha == TRILHA_PADRAO:
        return ARQ_BANCO
    return config.arq_banco(trilha)


@contextmanager
def conectar(trilha: str | None = None):
    caminho = _caminho(trilha)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
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
def registrar_resposta(sessao_id: str, pergunta: dict, acertou: bool, trilha: str | None = None):
    with conectar(trilha) as con:
        con.execute(
            "INSERT INTO respostas (sessao_id, area, enunciado, correta, fonte_titulo, fonte_url, respondida_em) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sessao_id, pergunta["area"], pergunta["enunciado"], int(acertou),
             pergunta["fonte"]["titulo"], pergunta["fonte"]["url"], _agora()),
        )


def respostas_do_aluno(sessao_id: str, trilha: str | None = None) -> list[dict]:
    with conectar(trilha) as con:
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


def salvar_pergunta(p: dict, status: str = "pendente", trilha: str | None = None) -> int | None:
    """Salva uma pergunta gerada pela IA. Ignora duplicadas (mesmo enunciado)."""
    with conectar(trilha) as con:
        cur = con.execute(
            "INSERT OR IGNORE INTO perguntas (area, enunciado, alternativas, correta, explicacao, "
            "fonte_titulo, fonte_url, status, criada_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (p["area"], p["enunciado"], json.dumps(p["alternativas"], ensure_ascii=False), p["correta"],
             p["explicacao"], p["fonte"]["titulo"], p["fonte"]["url"], status, _agora()),
        )
        return cur.lastrowid if cur.rowcount else None


def perguntas_aprovadas(area: str | None, quantidade: int, evitar: set[str] = frozenset(),
                        trilha: str | None = None) -> list[dict]:
    """Sorteia perguntas já aprovadas por humano, evitando as que o aluno já respondeu."""
    sql = "SELECT * FROM perguntas WHERE status = 'aprovada'"
    params: list = []
    if area:
        sql += " AND area = ?"
        params.append(area)
    sql += " ORDER BY RANDOM()"
    with conectar(trilha) as con:
        todas = [_linha_para_pergunta(l) for l in con.execute(sql, params)]
    novas = [p for p in todas if p["enunciado"] not in evitar]
    return (novas or todas)[:quantidade]


def obter_pergunta(pergunta_id: int, trilha: str | None = None) -> dict | None:
    with conectar(trilha) as con:
        l = con.execute("SELECT * FROM perguntas WHERE id = ?", (pergunta_id,)).fetchone()
        return _linha_para_pergunta(l) if l else None


def perguntas_por_status(status: str = "pendente", trilha: str | None = None) -> list[dict]:
    with conectar(trilha) as con:
        return [_linha_para_pergunta(l) for l in con.execute("SELECT * FROM perguntas WHERE status = ? ORDER BY id", (status,))]


def definir_status(pergunta_id: int, status: str, trilha: str | None = None):
    with conectar(trilha) as con:
        con.execute("UPDATE perguntas SET status = ? WHERE id = ?", (status, pergunta_id))


def resumo_banco(trilha: str | None = None) -> dict:
    with conectar(trilha) as con:
        linhas = con.execute("SELECT area, status, COUNT(*) AS n FROM perguntas GROUP BY area, status")
        resumo: dict = {}
        for l in linhas:
            resumo.setdefault(l["area"], {})[l["status"]] = l["n"]
        return resumo


# ── Histórico do chat ───────────────────────────────────────────────────────
def salvar_mensagem(sessao_id: str, papel: str, texto: str, extra: dict | None = None, trilha: str | None = None):
    with conectar(trilha) as con:
        con.execute(
            "INSERT INTO mensagens (sessao_id, papel, texto, extra, criada_em) VALUES (?, ?, ?, ?, ?)",
            (sessao_id, papel, texto, json.dumps(extra, ensure_ascii=False) if extra else None, _agora()),
        )


def mensagens_da_sessao(sessao_id: str, limite: int = 50, trilha: str | None = None) -> list[dict]:
    """Últimas mensagens da conversa, da mais antiga para a mais nova."""
    with conectar(trilha) as con:
        linhas = con.execute(
            "SELECT papel, texto, extra, criada_em FROM mensagens WHERE sessao_id = ? ORDER BY id DESC LIMIT ?",
            (sessao_id, limite),
        ).fetchall()
    return [{"papel": l["papel"], "texto": l["texto"], "extra": json.loads(l["extra"]) if l["extra"] else {},
             "criada_em": l["criada_em"]} for l in reversed(linhas)]


def apagar_mensagens(sessao_id: str, trilha: str | None = None):
    with conectar(trilha) as con:
        con.execute("DELETE FROM mensagens WHERE sessao_id = ?", (sessao_id,))
