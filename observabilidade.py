"""
observabilidade.py — REGISTRO de cada interação (logs estruturados).

Cada pergunta respondida vira UMA linha JSON em data/logs/interacoes.jsonl:
  quando, canal, tipo, ferramentas, nº de fontes, tokens, tempo, modelo e erro (se houve).

Por que JSONL? Uma linha = um evento. Fácil de ler com Python, Excel/Power BI ou
de enviar depois para Grafana/Loki, Azure Monitor etc.

Privacidade: a pergunta é guardada só com os primeiros 200 caracteres e o arquivo
fica fora do Git (pasta data/). Ver docs/11-seguranca-e-etica.md.

Veja o resumo com:  python relatorio.py
"""
import json
from datetime import datetime

from config import ARQ_LOG, PRECO_REF_ENTRADA_1M, PRECO_REF_SAIDA_1M


def custo_referencia(tokens_entrada: int, tokens_saida: int) -> float:
    """Quanto custaria em US$ numa API paga (preço de referência do config). O custo real aqui é zero."""
    return (tokens_entrada * PRECO_REF_ENTRADA_1M + tokens_saida * PRECO_REF_SAIDA_1M) / 1_000_000


def registrar(canal: str, **dados):
    """Grava um evento. Nunca derruba o tutor: se o log falhar, a resposta segue normalmente."""
    evento = {"quando": datetime.now().isoformat(timespec="seconds"), "canal": canal, **dados}
    if "pergunta" in evento:
        evento["pergunta"] = str(evento["pergunta"])[:200]
    try:
        ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ARQ_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except OSError:
        pass


def ler_eventos() -> list[dict]:
    if not ARQ_LOG.exists():
        return []
    eventos = []
    with open(ARQ_LOG, encoding="utf-8") as f:
        for linha in f:
            try:
                eventos.append(json.loads(linha))
            except json.JSONDecodeError:
                continue  # linha corrompida não impede o relatório
    return eventos
