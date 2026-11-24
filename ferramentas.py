"""
ferramentas.py — As FERRAMENTAS que o agente pode decidir usar (tool use / function calling).

Cada ferramenta tem:
  1. um "cartão de descrição" (schema JSON) que o LLM lê para decidir quando usá-la;
  2. uma função Python que executa de verdade.

As áreas disponíveis para o simulado vêm da TRILHA (certificação) da sessão.
"""
import json

import progresso
import simulado
import trilhas
from config import TRILHA_PADRAO
from rag import lista_fontes, montar_contexto, recuperar
from sessao import Sessao


def areas_da_trilha(trilha_id: str = TRILHA_PADRAO) -> list[str]:
    return trilhas.obter(trilha_id).nomes_areas


# ── 1. Cartões de descrição (o LLM lê isto) ───────────────────────────────
def ferramentas_da_trilha(trilha_id: str = TRILHA_PADRAO) -> list[dict]:
    t = trilhas.obter(trilha_id)
    areas = t.nomes_areas
    return [
        {
            "type": "function",
            "function": {
                "name": "buscar_documentacao",
                "description": f"Busca trechos da documentação oficial sobre {t.provedor} e o conteúdo do "
                               f"exame {t.sigla}. Use SEMPRE que o aluno tiver uma dúvida, pedir explicação, "
                               "definição ou comparação de conceitos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consulta": {"type": "string",
                                     "description": "O que buscar, em português. Inclua o nome do serviço "
                                                    "ou conceito."},
                    },
                    "required": ["consulta"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "gerar_simulado",
                "description": f"Gera perguntas de múltipla escolha no estilo do exame {t.sigla}. Use quando o "
                               "aluno pedir simulado, quiz, teste, exercício ou perguntas para praticar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area": {"type": "string", "enum": areas + ["Todas"],
                                 "description": "Área do exame. Use 'Todas' se o aluno não especificar."},
                        "quantidade": {"type": "integer", "minimum": 1, "maximum": 5,
                                       "description": "Número de perguntas (padrão 3)."},
                    },
                    "required": ["area"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ver_progresso",
                "description": "Mostra o desempenho do aluno por área do exame e o que estudar a seguir. "
                               "Use quando o aluno perguntar como está indo, seu progresso, desempenho, "
                               "pontos fracos ou o que deve estudar.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


# Compatibilidade: ferramentas e áreas da trilha padrão
AREAS = areas_da_trilha()
FERRAMENTAS = ferramentas_da_trilha()


# ── 2. Execução ───────────────────────────────────────────────────────────
def executar(nome: str, argumentos: str | dict, sessao: Sessao) -> dict:
    """Executa a ferramenta pedida pelo LLM, sempre no contexto da trilha da sessão.
    Retorna:
      conteudo        → texto devolvido ao LLM para ele escrever a resposta
      exibir_direto   → texto mostrado direto ao aluno, sem passar pelo LLM
      fontes, uso     → metadados para a resposta final
    """
    if isinstance(argumentos, str):
        try:
            argumentos = json.loads(argumentos or "{}")
        except json.JSONDecodeError:
            argumentos = {}

    areas = areas_da_trilha(sessao.trilha)

    if nome == "buscar_documentacao":
        trechos = recuperar(argumentos.get("consulta", ""), sessao.trilha)
        if not trechos:
            return {"conteudo": "Nenhum trecho relevante encontrado na documentação oficial.", "fontes": []}
        return {"conteudo": montar_contexto(trechos), "fontes": lista_fontes(trechos)}

    if nome == "gerar_simulado":
        area = argumentos.get("area")
        area = area if area in areas else None  # "Todas" ou valor inválido → todas as áreas
        qtd = argumentos.get("quantidade") or 3
        qtd = max(1, min(5, int(qtd))) if str(qtd).isdigit() else 3
        perguntas, uso = simulado.obter_perguntas(sessao, area, qtd)
        if not perguntas:
            return {"exibir_direto": "Ainda não há perguntas aprovadas para essa área. "
                                     "Rode `python importar_perguntas.py` para carregar o banco inicial.", "uso": uso}
        return {"exibir_direto": simulado.iniciar(sessao, perguntas), "uso": uso,
                "pergunta": {k: v for k, v in sessao.pergunta_atual.items() if k not in ("correta", "explicacao")}}

    if nome == "ver_progresso":
        dados = progresso.calcular(sessao.sessao_id, sessao.trilha)
        return {"exibir_direto": progresso.formatar(dados), "progresso": dados}

    return {"conteudo": f"Ferramenta desconhecida: {nome}"}
