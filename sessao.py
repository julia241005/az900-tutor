"""
sessao.py — MEMÓRIA do agente.

Cada aluno (sessão) tem:
  - histórico da conversa (memória de curto prazo, para entender "e o ZRS?")
  - simulado em andamento (fila de perguntas e a pergunta atual)
  - resultados das respostas (base do painel de progresso da Fase 4)

O histórico é salvo no SQLite (tabela mensagens): ao reabrir o tutor, a conversa continua.
Ao LLM vão só as últimas MAX_HISTORICO mensagens (controla tamanho e custo do prompt).
O simulado em andamento fica só em memória. Os resultados vão para o banco (banco.py).
"""
from dataclasses import dataclass, field

import banco

MAX_HISTORICO = 10  # últimas mensagens enviadas ao LLM


@dataclass
class Sessao:
    sessao_id: str = "terminal"
    historico: list = field(default_factory=list)
    simulado: list = field(default_factory=list)   # perguntas ainda não respondidas
    pergunta_atual: dict | None = None
    acertos_rodada: int = 0
    total_rodada: int = 0
    resultados: list = field(default_factory=list)  # resultados desta execução (os permanentes ficam no banco)

    def lembrar(self, papel: str, texto: str, extra: dict | None = None):
        self.historico.append({"role": papel, "content": texto})
        self.historico = self.historico[-MAX_HISTORICO:]
        banco.salvar_mensagem(self.sessao_id, papel, texto, extra)


_SESSOES: dict[str, Sessao] = {}


def obter_sessao(sessao_id: str) -> Sessao:
    """Devolve a sessão; se o tutor acabou de abrir, recarrega o histórico salvo no banco."""
    if sessao_id not in _SESSOES:
        salvas = banco.mensagens_da_sessao(sessao_id, MAX_HISTORICO)
        _SESSOES[sessao_id] = Sessao(
            sessao_id=sessao_id,
            historico=[{"role": m["papel"], "content": m["texto"]} for m in salvas],
        )
    return _SESSOES[sessao_id]


def nova_conversa(sessao_id: str):
    """Apaga o histórico da conversa (o progresso no simulado continua guardado)."""
    banco.apagar_mensagens(sessao_id)
    _SESSOES.pop(sessao_id, None)
