# 05 · Recuperação e RAG

> **Objetivo:** gerar respostas didáticas, fiéis à documentação oficial e com citação de fontes.
> **Arquivos no código:** [`rag.py`](../rag.py) e [`api.py`](../api.py)
> **Comandos:** `python rag.py "sua pergunta"` · `uvicorn api:app --reload`

## O que é RAG?

**RAG (Retrieval-Augmented Generation)** = Recuperação + Aumento + Geração.
Em vez de confiar só no que o LLM "lembra", o sistema **busca a informação oficial primeiro** e entrega ao LLM junto com a pergunta.

```
pergunta ──► R: busca trechos (ChromaDB) ──► filtro de relevância
                                                   │
                       ┌───────────────────────────┘
                       ▼
            A: monta o prompt  =  regras (prompt de sistema) + trechos numerados + pergunta
                       │
                       ▼
            G: LLM gera a resposta em streaming, citando [1], [2]...
                       │
                       ▼
            resposta + fontes + tokens + tempo
```

## Por que RAG e não só o LLM?

| Só o LLM | Com RAG |
|---|---|
| Pode inventar (alucinar) | Responde com base em trechos oficiais |
| Conhecimento congelado na data do treino | Atualiza recoletando a documentação |
| Não mostra a origem | Cita a fonte com link |
| Modelo pequeno sabe pouco de Azure | Modelo pequeno + bons trechos = boa resposta |

## Componentes

### 1. Recuperação com filtro de relevância
- Busca os `TOP_K = 4` trechos mais parecidos.
- Descarta trechos com similaridade abaixo de `SIMILARIDADE_MINIMA = 0.30`.
- **Se nenhum trecho passar, o LLM nem é chamado:** o tutor responde que não encontrou na documentação. Isso evita respostas inventadas e economiza processamento.

### 2. Prompt de sistema (guardrails)
Define o papel e as regras do tutor:
- responder **somente** com base nos trechos;
- citar as fontes com `[n]`;
- admitir quando não souber;
- português do Brasil, didático, com "💡 Dica para a prova";
- recusar assuntos fora do AZ-900.

### 3. Geração
| Parâmetro | Valor | Motivo |
|---|---|---|
| Modelo | `qwen2.5:3b` via Ollama | Gratuito, local, bom em português, suporta ferramentas (Fase 3) |
| Temperatura | 0.2 | Respostas mais fiéis e consistentes |
| Máx. tokens | 700 | Respostas objetivas |
| Streaming | Sim | O texto aparece aos poucos (melhor experiência) |

### 4. Métricas por resposta
Cada resposta registra **tokens de entrada, tokens de saída e tempo**. Hoje o custo é US$ 0 (modelo local), mas as métricas permitem estimar quanto custaria com uma API paga (doc 09, FinOps de IA).

## Provedor do LLM (sem custo)

O código usa o **formato de API da OpenAI**, que o Ollama também aceita. Para trocar de modelo ou provedor, basta alterar no `.env`:

```
LLM_URL=http://localhost:11434/v1
LLM_MODELO=qwen2.5:3b
LLM_CHAVE=ollama
```

## API (FastAPI)

| Rota | Método | Função |
|---|---|---|
| `/saude` | GET | Verifica se a API está no ar |
| `/perguntar` | POST | Resposta completa (JSON) |
| `/perguntar/stream` | POST | Resposta em streaming (Server-Sent Events) |

Documentação interativa automática: `http://localhost:8000/docs`

**Exemplo de evento do streaming:**
```
data: {"tipo": "texto", "conteudo": "O GRS copia..."}
data: {"tipo": "fim", "resposta": "...", "fontes": [...], "tokens_entrada": 1100, "tokens_saida": 220, "segundos": 8.4}
```

## Limitações conhecidas
- Modelo de 3B parâmetros: pode errar em perguntas complexas ou misturar conceitos. Será medido na avaliação (doc 08).
- Respostas mais lentas que APIs na nuvem, dependendo do computador.
- Ainda não há memória de conversa (vem na Fase 3).
