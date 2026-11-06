# 08 · Atualização da base

> **Objetivo:** manter o tutor em dia com a documentação oficial, que a Microsoft atualiza com frequência.
> **Arquivos no código:** [`atualizar_base.py`](../atualizar_base.py), [`ingestao/`](../ingestao/)

## Por que atualizar

Um RAG só é tão bom quanto a sua base. Se a Microsoft muda o nome de um serviço (como Azure AD → Microsoft Entra ID) ou o conteúdo do exame, o tutor precisa reler as páginas. Senão ele cita uma informação desatualizada **com a fonte oficial ao lado**, o que é pior do que não responder.

## A rotina

```
python atualizar_base.py
```

```
fotografia das páginas atuais (hash de cada texto)
        │
        ▼
coletar  ──► compara: páginas novas · alteradas · iguais
        │
        ├─ nada mudou → mantém o índice (economiza tempo)
        └─ mudou      → fragmentar → indexar (recria a coleção do zero, sem duplicar)
        │
        ▼
reiniciar o tutor  →  python avaliar.py  (a qualidade se manteve?)
```

- **Hash (SHA-256):** uma "impressão digital" do texto. Se uma vírgula muda, o hash muda. Assim o script sabe exatamente quais páginas foram alteradas.
- **Recriar do zero:** mais simples e seguro do que atualizar pedaço por pedaço. Com ~1.000 fragmentos leva poucos minutos.
- **Avaliar depois:** toda mudança na base pode mudar a qualidade. O conjunto de avaliação (doc 09) mostra se piorou.

## Quando rodar

| Situação | Ação |
|---|---|
| Uma vez por mês | `python atualizar_base.py` |
| Microsoft anunciou mudança no exame (guia de estudo novo) | revisar `ingestao/fontes.py` + atualizar |
| Uma página nova importante | adicionar em `fontes.py` + atualizar |

## O que fica fora do Git

`data/` (páginas baixadas, fragmentos, índice e banco) fica no `.gitignore`: o conteúdo é da Microsoft e pode ser recriado a qualquer momento com esta rotina.
