"""
sessao.py — MEMÓRIA do agente.

Cada aluno (sessão) tem:
  - histórico da conversa (memória de curto prazo, para entender "e o ZRS?")
  - simulado em andamento (fila de perguntas e a pergunta atual)
  - resultados das respostas (base do painel de progresso da Fase 4)

O histórico e o simulado em andamento ficam em memória (curto prazo).
Os resultados vão para o banco SQLite (longo prazo) — ver banco.py e progresso.py.
"""
from dataclasses import dataclass, field

MAX_HISTORICO = 10  # últimas mensagens enviadas ao LLM (controla tamanho e custo do prompt)


@dataclass
class Sessao:
    sessao_id: str = "terminal"
    historico: list = field(default_factory=list)
    simulado: list = field(default_factory=list)   # perguntas ainda não respondidas
    pergunta_atual: dict | None = None
    acertos_rodada: int = 0
    total_rodada: int = 0
    resultados: list = field(default_factory=list)  # resultados desta execução (os permanentes ficam no banco)

    def lembrar(self, papel: str, texto: str):
        self.historico.append({"role": papel, "content": texto})
        self.historico = self.historico[-MAX_HISTORICO:]


_SESSOES: dict[str, Sessao] = {}


def obter_sessao(sessao_id: str) -> Sessao:
    if sessao_id not in _SESSOES:
        _SESSOES[sessao_id] = Sessao(sessao_id=sessao_id)
    return _SESSOES[sessao_id]
