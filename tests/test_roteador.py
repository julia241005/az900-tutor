"""Roteador: decide sem IA se a mensagem é dúvida, simulado, progresso ou conversa."""
import pytest

import roteador
from ingestao.fontes import AREA_ARQUITETURA, AREA_GOVERNANCA


@pytest.mark.parametrize("mensagem", [
    "Qual a diferença entre LRS e GRS?",
    "Como funciona o ExpressRoute?",
    "Como vou conectar minha rede local ao Azure?",
    "E o ZRS?",
    "Quais perguntas costumam cair sobre Azure Policy?",
])
def test_duvidas_vao_para_a_documentacao(mensagem):
    assert roteador.decidir(mensagem)[0] == "duvida"


def test_pedido_de_simulado_com_area_e_quantidade():
    intencao, args = roteador.decidir("Me faz um simulado de governança com 4 perguntas")
    assert intencao == "gerar_simulado"
    assert args == {"area": AREA_GOVERNANCA, "quantidade": 4}


def test_simulado_sem_area_usa_todas():
    assert roteador.decidir("quero um quiz")[1] == {"area": "Todas", "quantidade": 3}
    assert roteador.decidir("simulado de rede")[1]["area"] == AREA_ARQUITETURA


@pytest.mark.parametrize("mensagem", ["Como estou indo?", "meu progresso", "O que devo estudar agora?"])
def test_progresso(mensagem):
    assert roteador.decidir(mensagem)[0] == "ver_progresso"


@pytest.mark.parametrize("mensagem", ["oi", "Olá!", "obrigada", "valeu!", "tchau"])
def test_conversa_simples_responde_sem_ia(mensagem):
    assert roteador.decidir(mensagem)[0] == "conversa"
    assert roteador.resposta_conversa(mensagem)
