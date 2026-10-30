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

## Custos

Essa etapa é **gratuita**: o modelo roda no computador local. O custo com tokens só começa na Fase 2, quando o LLM entra.

## Evoluções possíveis

- Testar modelos de embedding maiores e comparar com a avaliação (doc 08).
- Busca híbrida (semântica + palavra-chave) para siglas como "LRS" e "GRS".
- Migrar para um banco vetorial em nuvem (ex.: Azure AI Search) na publicação.
