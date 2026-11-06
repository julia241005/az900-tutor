# 10 · Custo, tokens e observabilidade (FinOps de IA)

> **Objetivo:** saber o que o tutor faz, quanto tempo leva e quanto custaria em escala.
> **Arquivos no código:** [`observabilidade.py`](../observabilidade.py), [`relatorio.py`](../relatorio.py), [`config.py`](../config.py)

## Observabilidade: registrar cada interação

Cada mensagem respondida vira **uma linha JSON** em `data/logs/interacoes.jsonl`:

```json
{"quando": "2026-11-04T10:12:03", "canal": "agente", "sessao": "web", "pergunta": "O que é ZRS?",
 "tipo": "resposta", "ferramentas": ["buscar_documentacao"], "fontes": 4,
 "tokens_entrada": 1050, "tokens_saida": 180, "segundos": 28.4, "modelo": "qwen2.5:3b"}
```

Erros também são registrados (`"erro": "ia_indisponivel"`, `"erro": "limite_de_mensagens"`).

- **Por que JSONL:** uma linha = um evento. Dá para ler com Python, abrir no Excel/Power BI ou enviar depois para Grafana/Loki ou Azure Monitor sem mudar nada.
- **O log nunca derruba o tutor:** se gravar falhar, a resposta segue normalmente.

## Relatório

```
python relatorio.py            # todo o histórico
python relatorio.py --dias 7   # última semana
```

Mostra: interações, erros, tipos (resposta, simulado, progresso), ferramentas mais usadas, respostas sem fonte, **tempo médio e p95** e **tokens e custo**.

> **p95:** o tempo que 95% das respostas não ultrapassam. A média esconde as respostas lentas; o p95 mostra o que o usuário sente nos piores casos.

## Custo: real × referência

| | Valor |
|---|---|
| **Custo real** | **US$ 0,00**: LLM e embeddings rodam no computador (Ollama + sentence-transformers) |
| **Custo de referência** | Quanto custaria a mesma quantidade de tokens numa API paga |

O preço de referência fica no `config.py` (ou no `.env`): `PRECO_REF_ENTRADA_1M` e `PRECO_REF_SAIDA_1M`, em US$ por 1 milhão de tokens. Os valores padrão (0,15 e 0,60) são **hipotéticos**: ajuste com o preço atual do provedor que quiser comparar.

### Unit economics

- **Custo por pergunta** = tokens de entrada × preço de entrada + tokens de saída × preço de saída
- **Custo por aluno** = custo total ÷ sessões
- Uma resposta do RAG usa cerca de **1.200 tokens** (medido na avaliação). A maior parte é **entrada**: os 4 trechos oficiais enviados ao modelo.

### Onde estão as alavancas de custo

| Alavanca | Efeito |
|---|---|
| `TOP_K` (trechos por pergunta) | Menos trechos = menos tokens de entrada, mas pode perder a fonte certa (ver doc 09) |
| `TAMANHO_FRAGMENTO` | Fragmentos menores = prompt menor |
| `MAX_HISTORICO` | Quantas mensagens anteriores vão junto em cada pergunta |
| Simulado sem IA | Perguntas aprovadas do banco: **zero tokens** |
| Correção por código | Corrigir A/B/C/D não chama o LLM: **zero tokens** |
| Limite de mensagens por minuto | Teto de gasto por usuário (doc 11) |

Essas decisões são o mesmo raciocínio de FinOps aplicado à nuvem: **medir, atribuir custo a uma unidade (pergunta, aluno) e otimizar**.
