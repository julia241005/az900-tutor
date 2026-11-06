# 04 · Embeddings e indexação

> **Objetivo:** permitir buscar trechos pelo **significado**, não só por palavra exata.
> **Arquivos no código:** [`ingestao/indexar.py`](../ingestao/indexar.py) e [`buscar.py`](../buscar.py)
> **Comandos:** `python -m ingestao.indexar` e `python buscar.py "sua pergunta"`

## O que é um embedding?

É a conversão de um texto em um **vetor** (lista de números) que representa o seu significado. Textos com sentido parecido geram vetores próximos.

Exemplo: *"replicação em outra região"* e *"armazenamento com redundância geográfica"* têm palavras diferentes, mas vetores próximos. Por isso a busca encontra um a partir do outro.

## Escolhas

| Item | Escolha | Motivo |
|---|---|---|
| Modelo | `paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers) | Gratuito, roda localmente, entende português, leve |
| Dimensão | 384 números por fragmento | Equilíbrio entre qualidade e tamanho |
| Normalização | Vetores normalizados | Permite usar similaridade de cosseno |
| Banco vetorial | ChromaDB (local, salvo em `data/vetores/`) | Simples, sem servidor, ideal para começar |
| Métrica | Cosseno | Padrão para comparar significado de textos |

## Fluxo

```
fragmentos.jsonl ──► modelo de embeddings ──► vetores ──► ChromaDB (com metadados)

pergunta ──► mesmo modelo ──► vetor ──► busca os K mais próximos ──► trechos + fontes
```

> A pergunta **precisa** usar o mesmo modelo dos fragmentos; caso contrário, os vetores não são comparáveis.

## Busca (Retrieval)

- `TOP_K = 4`: retorna os 4 trechos mais parecidos.
- Filtro opcional por área do exame (`area`).
- Retorna o texto, a similaridade (0 a 1) e os metadados para citação.

## Busca híbrida (Fase 6)

A busca por significado entende sinônimos ("copiar dados para outra região" ≈ "replicação geográfica"), mas modelos de embedding pequenos representam mal **siglas e nomes próprios** (LRS, GRS, CapEx, Acesso Condicional). A busca híbrida junta os dois mundos:

```
pergunta ──┬─► embeddings (significado) ──► top 20 por similaridade ──┐
           │                                                          ├─► RRF ──► top 4
           └─► BM25 (palavra exata)       ──► top 20 por palavras ────┘
```

- **BM25:** algoritmo clássico de buscadores. Dá mais pontos a palavras raras (como "GRS") do que a palavras comuns. Siglas digitadas em maiúsculas ganham **peso 3×**. Acentos e maiúsculas são ignorados.
- **RRF (Reciprocal Rank Fusion):** junta as duas listas pela **posição** de cada trecho (1 ÷ (60 + posição)). Não precisa comparar notas de escalas diferentes.
- **Filtro de relevância:** o trecho é mantido se a similaridade for ≥ 0,30 **ou** se tiver palavra exata em comum com a pergunta.
- **Resultado medido:** acerto@4 de 93% → 97% e MRR de 0,80 → 0,90 (doc 09).
- Para comparar: `MODO_BUSCA=vetorial` no `.env` volta ao modo antigo.

## Custos

Essa etapa é **gratuita**: o modelo roda no computador local. O custo com tokens só começa na Fase 2, quando o LLM entra.

## Evoluções possíveis

- Testar modelos de embedding maiores e comparar com a avaliação (doc 09).
- ~~Busca híbrida (semântica + palavra-chave)~~ ✅ feita na Fase 6.
- Reranqueador (cross-encoder) para reordenar os trechos finais.
- Migrar para um banco vetorial em nuvem (ex.: Azure AI Search) na publicação.
