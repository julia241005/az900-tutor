# 09 · Avaliação de qualidade (evals)

> **Objetivo:** provar com números que o tutor acerta e usar esses números para melhorar.
> **Arquivos no código:** [`avaliar.py`](../avaliar.py), [`avaliacao/conjunto.json`](../avaliacao/conjunto.json), [`avaliacao/resultados/`](../avaliacao/resultados/), [`tests/`](../tests/)

## Por que avaliar

"Testei umas perguntas e pareceu bom" não é medida. Em produtos de IA, cada mudança (prompt, modelo, tamanho do fragmento, tipo de busca) pode melhorar uma coisa e piorar outra. Um **conjunto fixo de perguntas** com resposta conhecida permite comparar antes e depois.

## O conjunto de avaliação

`avaliacao/conjunto.json` tem **33 perguntas**:

- **30 de conteúdo**, 10 por área do exame. Cada uma diz qual página oficial é a fonte certa e quais termos uma boa resposta deve ter.
- **3 fora do escopo** (receita de bolo, futebol). O tutor deve **recusar** em vez de inventar.

## Duas camadas de avaliação

### 1. Busca (rápida, sem LLM)

```
python avaliar.py
```

| Métrica | O que mede |
|---|---|
| **Acerto@k** | Em quantas perguntas a fonte certa veio entre os k trechos (k = `TOP_K` = 4) |
| **MRR** (Mean Reciprocal Rank) | Quão no topo a fonte certa veio: 1º lugar = 1, 2º = 0,5, 3º = 0,33... (média) |

### 2. Respostas (lenta, usa o LLM)

```
python avaliar.py --completo          # ~30 s por pergunta com qwen2.5:3b
python avaliar.py --completo --juiz   # + LLM como avaliador
```

| Métrica | O que mede |
|---|---|
| **Termos esperados** | % dos termos-chave que aparecem na resposta |
| **Cita as fontes** | A resposta usa [1], [2]... |
| **Fonte certa citada** | A página certa está entre as fontes mostradas |
| **Recusa fora do escopo** | Nas perguntas de bolo/futebol, o tutor recusou |
| **Fiel aos trechos (juiz)** | Outro LLM confere se a resposta só diz o que está nos trechos |

> **LLM como juiz (LLM-as-judge):** técnica comum para avaliar texto em escala. Com um modelo pequeno avaliando a si mesmo o resultado é só indicativo. Em produção usa-se um modelo maior como juiz, ou revisão humana por amostragem.

## Resultados

### Busca: vetorial × híbrida (04/11/2026, 30 perguntas, TOP_K = 4)

| Modo | Acerto@4 | MRR |
|---|---|---|
| Vetorial (só significado) | 93% | 0,80 |
| **Híbrida (significado + palavra exata)** | **97%** | **0,90** |

**Análise:**

- A busca vetorial errou **"CapEx e OpEx"** e **"Acesso Condicional"**: siglas e nomes próprios, que modelos de embedding pequenos representam mal. A busca por palavra exata (BM25) resolve esses casos.
- A híbrida errou só **"alta disponibilidade e SLA"**: "disponibilidade" aparece em muitas páginas (zonas de disponibilidade, conjuntos de disponibilidade), o que dilui a busca.
- Além de acertar mais, a híbrida coloca a fonte certa **mais no topo** (MRR 0,80 → 0,90). Isso importa porque o LLM dá mais peso ao primeiro trecho.
- **Decisão:** `MODO_BUSCA = "hibrida"` passa a ser o padrão.

### Respostas (qwen2.5:3b)

**Rodada 1 (prompt original):**

| Métrica | Resultado |
|---|---|
| Fonte certa entre as citadas | 97% |
| Recusa fora do escopo (bolo, futebol) | 100% |
| Termos esperados presentes | 70% (contando recusas como 0) |
| Cita as fontes [1], [2]... | 70% |
| **Recusa indevida** | **13%** (4 de 30) |
| Tempo médio / tokens médios | 24 s / 1.320 tokens |

**O que a análise das respostas mostrou:**

- **Recusa indevida:** em 4 perguntas ("LRS e GRS", "escalabilidade vertical e horizontal", "ExpressRoute", "calculadora de preços e TCO") a busca trouxe a fonte certa, mas o modelo respondeu "não encontrei". Três delas são **comparações**: cada trecho explicava um lado, e a regra "se os trechos não tiverem a resposta, diga que não encontrou" fez o modelo pequeno desistir.
- **Erro de conteúdo:** na responsabilidade compartilhada, o modelo disse que VMs e sistema operacional são sempre do cliente. O certo são dados, contas e dispositivos. A fonte certa estava lá: foi falha de leitura do modelo de 3B.
- **Métrica a corrigir:** duas respostas certas tiraram 0 em termos esperados porque o modelo usou "Exclusão" em vez de "excluir". Os termos passaram a usar radicais ("exclu", "leitura").
- **Citação:** às vezes o modelo copiava a linha "Fonte: ..." do trecho em vez de citar [1].

**Ajuste feito:** a regra 3 do prompt passou a dizer "se a resposta estiver nos trechos, **mesmo que em partes**, junte as partes e responda; só diga que não encontrou quando **nenhum** trecho tratar do assunto", e a regra 2 pede a citação no fim das frases, sem copiar a linha "Fonte:".

**Rodada 2 (prompt ajustado):**

_Pendente: rodar `python avaliar.py --completo` com o prompt ajustado e registrar aqui a comparação com a rodada 1 (principalmente a recusa indevida)._

## Testes automáticos (pytest)

Avaliação mede **qualidade**. Testes garantem que **nada quebrou**:

```
python -m pytest -q      # 27 testes, ~15 s, não precisa do Ollama
```

| Arquivo | O que garante |
|---|---|
| `test_busca.py` | Palavras, siglas, BM25 e fusão de rankings |
| `test_memoria.py` | Histórico salvo, nova conversa, correção do simulado, embaralhamento correto |
| `test_seguranca.py` | Senha e limite de mensagens |
| `test_observabilidade.py` | Log e cálculo de custo |
| `test_api.py` | Endpoints, erro claro sem o Ollama, gabarito nunca vai ao navegador |
| `test_avaliacao.py` | O conjunto de avaliação está bem formado |

Os testes usam banco e log **temporários**: nunca mexem no seu progresso real.
