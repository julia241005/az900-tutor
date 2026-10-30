# 06 · Agente e ferramentas

> **Objetivo:** o tutor deixa de só responder e passa a **decidir o que fazer**.
> **Arquivos no código:** [`agente.py`](../agente.py), [`ferramentas.py`](../ferramentas.py), [`simulado.py`](../simulado.py), [`sessao.py`](../sessao.py), [`chat.py`](../chat.py)
> **Comandos:** `python chat.py` · API: `POST /chat` e `POST /chat/stream`

## RAG × Agente

| RAG (Fase 2) | Agente (Fase 3) |
|---|---|
| Sempre faz a mesma coisa: busca → responde | O LLM **escolhe** a ação |
| Sem memória | Lembra a conversa ("e o ZRS?") |
| Só responde dúvidas | Responde, gera simulado e corrige |

## Fluxo

```
mensagem
   │
   ├─► É uma letra (A–D) e há simulado em andamento? ──► corrigir por CÓDIGO (sem IA)
   │
   ▼
LLM + prompt do agente + histórico + cartões das ferramentas
   │
   ├─ chamou buscar_documentacao ──► trechos oficiais ──► LLM escreve a resposta (streaming, cita [n])
   ├─ chamou gerar_simulado      ──► LLM gera perguntas em JSON ──► código valida/embaralha ──► mostra direto
   └─ não chamou ferramenta
          ├─ mensagem curta (ex.: "oi")  ──► resposta de conversa
          └─ parece dúvida (4+ palavras) ──► guardrail: força o RAG (nunca responde "de memória")
```

## Ferramentas

| Ferramenta | Quem decide | Quem executa | Por quê |
|---|---|---|---|
| `buscar_documentacao` | LLM | Código (busca vetorial) | Dúvidas sempre baseadas na documentação oficial |
| `gerar_simulado` | LLM | LLM (gera JSON) + código (valida) | Criar perguntas exige linguagem; validar exige precisão |
| `corrigir_resposta` | **Código** | **Código** | Correção não pode errar nem "alucinar" |

### Princípio de design: IA onde agrega, código onde precisa ser exato
O modelo usado é pequeno (3B parâmetros). Por isso:
- **decisões e textos** ficam com o LLM;
- **regras, correção e validação** ficam com o código.

Isso torna o agente mais **confiável, rápido e barato**, prática comum em sistemas de produção.

## Cartões de descrição (schemas)

O LLM não "vê" o código: ele lê uma **descrição em JSON** de cada ferramenta (nome, quando usar, parâmetros) e responde pedindo a ferramenta com os argumentos. Exemplo:

```json
{"name": "gerar_simulado", "arguments": {"area": "Gestão e governança do Azure", "quantidade": 2}}
```

O parâmetro `area` usa uma lista fechada (`enum`) com as 3 áreas oficiais. Valores inválidos são tratados como "Todas".

## Simulado

1. Sorteia trechos de conteúdo da área (o guia de estudo é excluído).
2. O LLM cria as perguntas em **JSON** (`response_format = json_object`).
3. O código **valida**: 4 alternativas (A–D), gabarito válido, enunciado presente. Perguntas inválidas são descartadas.
4. O código **embaralha as alternativas**, evitando o viés de o modelo colocar a correta sempre na "A".
5. As perguntas aparecem uma de cada vez. A correção mostra a explicação, a fonte oficial e, no fim, o placar comparado à meta de 80%.

## Memória (sessão)

- Cada `sessao_id` tem histórico, simulado em andamento e resultados.
- Só as **últimas 10 mensagens** vão para o LLM, o que controla tamanho do prompt, tempo e custo.
- Hoje fica em memória (some ao reiniciar). **Na Fase 4 vai para um banco de dados** e vira o painel de progresso.

## API

| Rota | Função |
|---|---|
| `POST /chat` | `{"sessao_id": "aluno-1", "mensagem": "..."}` → resposta completa |
| `POST /chat/stream` | Mesmo, em streaming (SSE) |

A resposta inclui: `resposta`, `tipo` (`resposta`, `simulado`, `correcao`, `conversa`), `ferramentas_usadas`, `fontes`, `pergunta` (sem gabarito, para o visual), tokens e tempo.

## Limitações conhecidas
- Modelos pequenos às vezes não chamam a ferramenta certa; o guardrail cobre o caso mais importante (dúvida sem busca).
- A geração de simulado é a etapa mais lenta no computador local.
- Busca ao vivo no Microsoft Learn (servidor MCP) fica como evolução futura.
