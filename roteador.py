"""
roteador.py — decide O QUE o agente vai fazer, por regras (sem chamar a IA).

Por que existe: antes, toda mensagem passava por DUAS chamadas ao LLM
(1ª para decidir a ferramenta, 2ª para responder). Na prática a decisão era quase
sempre "buscar na documentação". Com regras simples, a decisão é instantânea e o
LLM é chamado só uma vez → respostas bem mais rápidas, principalmente em CPU.

O modo antigo (o LLM decide) continua disponível: ROTEAMENTO=llm no .env.
Detalhes: docs/06-agente-e-ferramentas.md
"""
import re
import unicodedata

from ingestao.fontes import AREA_ARQUITETURA, AREA_CONCEITOS, AREA_GOVERNANCA


def _normalizar(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


CONVERSA = re.compile(
    r"^\s*(oi+|ola|e ai|bom dia|boa tarde|boa noite|obrigad[oa]|valeu|vlw|tchau|ate mais|ok|beleza|blz|"
    r"show|legal|perfeito|tudo bem\??|quem e voce\??|o que voce faz\??)[\s!.?]*$")
SIMULADO = re.compile(
    r"\b(simulado|quiz|questoes|questao|exercicios?|me (testa|teste)|"
    r"(faz|faca|fazer|quero|me da|manda|gera|gere)\b.{0,25}\bperguntas?|perguntas? (para|pra) (praticar|treinar))\b")
PROGRESSO = re.compile(
    r"\b(meu (progresso|desempenho|resultado)|como (eu )?(estou|to)( indo)?|como (eu )?vou indo|meus pontos fracos|"
    r"onde (eu )?(estou|to) (fraca|fraco|mal)|o que (eu )?(devo|preciso) (estudar|revisar))\b")

AREAS_POR_PALAVRA = [
    (re.compile(r"\b(governanca|gestao|custo|custos|policy|bloqueio|monitor|conformidade)\b"), AREA_GOVERNANCA),
    (re.compile(r"\b(arquitetura|servicos|rede|armazenamento|computacao|identidade|seguranca)\b"), AREA_ARQUITETURA),
    (re.compile(r"\b(conceitos?|nuvem|iaas|paas|saas)\b"), AREA_CONCEITOS),
]


def decidir(mensagem: str) -> tuple[str, dict]:
    """Retorna (intencao, argumentos). Intenções: conversa, gerar_simulado, ver_progresso, duvida."""
    t = _normalizar(mensagem)
    if CONVERSA.match(t):
        return "conversa", {}
    if PROGRESSO.search(t):
        return "ver_progresso", {}
    if SIMULADO.search(t):
        area = next((a for padrao, a in AREAS_POR_PALAVRA if padrao.search(t)), "Todas")
        numero = re.search(r"\b([1-9])\b", t)
        return "gerar_simulado", {"area": area, "quantidade": int(numero.group(1)) if numero else 3}
    return "duvida", {}


def resposta_conversa(mensagem: str) -> str:
    """Respostas prontas para conversa simples: instantâneas e sem gastar tokens."""
    t = _normalizar(mensagem)
    if re.search(r"obrigad|valeu|vlw", t):
        return "De nada! Se surgir outra dúvida sobre o AZ-900, é só perguntar."
    if re.search(r"tchau|ate mais", t):
        return "Até mais! Bons estudos. 💪"
    if re.search(r"quem e voce|o que voce faz", t):
        return ("Sou um tutor para o exame AZ-900. Explico conceitos com base na documentação oficial "
                "da Microsoft (sempre com as fontes), faço simulados e mostro seu progresso por área.")
    return "Olá! Posso explicar conceitos do AZ-900 com as fontes oficiais ou fazer um simulado com você. Por onde começamos?"
