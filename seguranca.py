"""
seguranca.py — PROTEÇÕES para quando o tutor sair do seu computador.

1. Senha (HTTP Basic): se TUTOR_SENHA estiver definida no .env, o navegador pede
   usuário e senha antes de abrir o tutor. Vazia = sem senha (uso local).
2. Limite de mensagens por minuto, por endereço IP: evita abuso e controla custo
   (numa API paga, cada mensagem custa dinheiro). Acima do limite → erro 429.

Detalhes: docs/11-seguranca-e-etica.md
"""
import base64
import secrets
import time
from collections import defaultdict, deque

from config import LIMITE_MENSAGENS_POR_MINUTO, TUTOR_SENHA

SENHA = TUTOR_SENHA


def senha_ok(cabecalho_authorization: str | None) -> bool:
    """Confere o cabeçalho 'Authorization: Basic ...'. O nome de usuário pode ser qualquer um."""
    if not SENHA:
        return True
    if not cabecalho_authorization or not cabecalho_authorization.startswith("Basic "):
        return False
    try:
        _usuario, _, senha = base64.b64decode(cabecalho_authorization[6:]).decode("utf-8").partition(":")
    except (ValueError, UnicodeDecodeError):
        return False
    return secrets.compare_digest(senha.encode(), SENHA.encode())  # comparação em tempo constante


class LimitadorDeTaxa:
    """Janela deslizante: guarda o horário das últimas mensagens de cada IP."""

    def __init__(self, limite: int = LIMITE_MENSAGENS_POR_MINUTO, janela_segundos: int = 60):
        self.limite = limite
        self.janela = janela_segundos
        self._registros: dict[str, deque] = defaultdict(deque)

    def permitir(self, chave: str, agora: float | None = None) -> bool:
        agora = time.monotonic() if agora is None else agora
        fila = self._registros[chave]
        while fila and agora - fila[0] >= self.janela:
            fila.popleft()
        if len(fila) >= self.limite:
            return False
        fila.append(agora)
        return True
