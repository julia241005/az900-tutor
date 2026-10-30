# 03 · Fragmentação (chunking)

> **Objetivo:** dividir os textos em pedaços pequenos e coerentes para a busca.
> **Arquivo no código:** [`ingestao/fragmentar.py`](../ingestao/fragmentar.py)
> **Comando:** `python -m ingestao.fragmentar`

## Por que fragmentar?

- O LLM tem limite de contexto e **cada token custa dinheiro**. Enviar páginas inteiras é caro e traz ruído.
- A busca fica mais precisa: um pedaço sobre "GRS" é encontrado com mais facilidade do que uma página inteira sobre armazenamento.

## Estratégia

1. **Por seção:** o texto é dividido nos títulos (`#`, `##`, `###`), mantendo cada assunto junto.
2. **Por tamanho:** seções maiores que `TAMANHO_FRAGMENTO` são cortadas em janelas, preferindo cortar no fim de frase ou de linha.
3. **Sobreposição:** cada pedaço repete o final do anterior, para que uma ideia cortada no meio apareça inteira em pelo menos um pedaço.
4. **Filtro:** pedaços com menos de 80 caracteres são descartados (pouca informação).

## Parâmetros (em `config.py`)

| Parâmetro | Valor | Equivalente aproximado |
|---|---|---|
| `TAMANHO_FRAGMENTO` | 1200 caracteres | ~300 tokens |
| `SOBREPOSICAO` | 200 caracteres | ~50 tokens |

Esses valores são um ponto de partida comum em RAG e serão **ajustados com base na avaliação** (doc 08).

## Metadados de cada fragmento

| Campo | Uso |
|---|---|
| `id` | Identificador único (URL + número) |
| `url`, `titulo`, `secao` | Citar a fonte na resposta |
| `area` | Filtrar por área do exame e medir desempenho |
| `tipo` | Diferenciar guia, treinamento e documentação |
| `coletado_em` | Controle de atualização |

**Saída:** `data/fragmentos.jsonl` (um fragmento por linha).
