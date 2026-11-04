"""
ferramentas.py — As FERRAMENTAS que o agente pode decidir usar (tool use / function calling).

Cada ferramenta tem:
  1. um "cartão de descrição" (schema JSON) que o LLM lê para decidir quando usá-la;
  2. uma função Python que executa de verdade.
"""
import json

import progresso
import simulado
from ingestao.fontes import AREA_ARQUITETURA, AREA_CONCEITOS, AREA_GOVERNANCA
from rag import lista_fontes, montar_contexto, recuperar
from sessao import Sessao

AREAS = [AREA_CONCEITOS, AREA_ARQUITETURA, AREA_GOVERNANCA]

# ── 1. Cartões de descrição (o LLM lê isto) ───────────────────────────────
FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_documentacao",
            "description": "Busca trechos da documentação oficial da Microsoft sobre Azure e computação "
                           "em nuvem. Use SEMPRE que o aluno tiver uma dúvida, pedir explicação, "
                           "definição ou comparação de conceitos do AZ-900.",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {"type": "string",
                                 "description": "O que buscar, em português. Inclua o nome do serviço "
                                                "ou conceito (ex.: 'diferença entre LRS e GRS')."},
                },
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "gerar_simulado",
            "description": "Gera perguntas de múltipla escolha no estilo do exame AZ-900. Use quando o "
                           "aluno pedir simulado, quiz, teste, exercício ou perguntas para praticar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area": {"type": "string", "enum": AREAS + ["Todas"],
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


# ── 2. Execução ───────────────────────────────────────────────────────────
def executar(nome: str, argumentos: str | dict, sessao: Sessao) -> dict:
    """Executa a ferramenta pedida pelo LLM.
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

    if nome == "buscar_documentacao":
        trechos = recuperar(argumentos.get("consulta", ""))
        if not trechos:
            return {"conteudo": "Nenhum trecho relevante encontrado na documentação oficial.", "fontes": []}
        return {"conteudo": montar_contexto(trechos), "fontes": lista_fontes(trechos)}

    if nome == "gerar_simulado":
        area = argumentos.get("area")
        area = area if area in AREAS else None  # "Todas" ou valor inválido → todas as áreas
        qtd = argumentos.get("quantidade") or 3
        qtd = max(1, min(5, int(qtd))) if str(qtd).isdigit() else 3
        perguntas, uso = simulado.obter_perguntas(sessao, area, qtd)
        if not perguntas:
            return {"exibir_direto": "Ainda não há perguntas aprovadas para essa área. "
                                     "Rode `python importar_perguntas.py` para carregar o banco inicial.", "uso": uso}
        return {"exibir_direto": simulado.iniciar(sessao, perguntas), "uso": uso,
                "pergunta": {k: v for k, v in sessao.pergunta_atual.items() if k not in ("correta", "explicacao")}}

    if nome == "ver_progresso":
        dados = progresso.calcular(sessao.sessao_id)
        return {"exibir_direto": progresso.formatar(dados), "progresso": dados}

    return {"conteudo": f"Ferramenta desconhecida: {nome}"}
