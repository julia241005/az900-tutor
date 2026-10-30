# ☁️ AZ-900 Tutor

Agente de IA que ajuda estudantes a se preparar para o exame **Microsoft Azure Fundamentals (AZ-900)**: explica conceitos com base na documentação oficial (com citação de fontes), gera simulados e acompanha o desempenho por área do exame.

## Arquitetura

```
┌───────────────────────────┐        ┌──────────────────────────────────────┐
│  FRONTEND                 │  API   │  BACKEND (Python)                    │
│  Next.js + Tailwind       │ ◄────► │  FastAPI · Agente · RAG · LLM        │
│  shadcn/ui + Framer Motion│        │  ChromaDB (banco vetorial)           │
└───────────────────────────┘        └──────────────────────────────────────┘
                                                      ▲
                                                      │ alimentação (pipeline)
                                     Microsoft Learn ─┘ coletar → fragmentar → indexar
```

## Progresso

| Fase | Entrega | Status |
|---|---|---|
| 1 · Alimentação | Coleta, limpeza, chunking, embeddings, busca | ✅ Concluída |
| 2 · RAG + API | LLM responde com fontes, via FastAPI com streaming | ⏳ |
| 3 · Agente | Ferramentas: buscar docs, gerar simulado, corrigir | ⏳ |
| 4 · Progresso | Desempenho por área + recomendação de estudo | ⏳ |
| 5 · Interface | Next.js + Tailwind + shadcn/ui (chat, simulado, painel) | ⏳ |
| 6 · Qualidade e custo | Avaliação automática + tokens/custo por pergunta | ⏳ |
| 7 · Publicação | Deploy (Vercel + Azure) e demo | ⏳ |

Passo a passo completo: [ROADMAP.md](ROADMAP.md)

## Documentação dos processos

| # | Processo | Status |
|---|---|---|
| 01 | [Fontes de dados](docs/01-fontes-de-dados.md) | ✅ |
| 02 | [Ingestão e limpeza](docs/02-ingestao-e-limpeza.md) | ✅ |
| 03 | [Fragmentação (chunking)](docs/03-fragmentacao.md) | ✅ |
| 04 | [Embeddings e indexação](docs/04-embeddings-e-indexacao.md) | ✅ |
| 05 | Recuperação e RAG | ⏳ Fase 2 |
| 06 | Banco de perguntas (human-in-the-loop) | ⏳ Fase 4 |
| 07 | Atualização da base | ⏳ Fase 6 |
| 08 | Avaliação de qualidade | ⏳ Fase 6 |
| 09 | Custo e tokens | ⏳ Fase 6 |
| 10 | Segurança e ética | ⏳ Fase 7 |

## Como rodar (Fase 1)

```bash
python -m venv venv
source venv/Scripts/activate        # Git Bash no Windows
pip install -r requirements.txt

python -m ingestao.coletar          # 1. baixa as páginas oficiais
python -m ingestao.fragmentar       # 2. quebra em pedaços
python -m ingestao.indexar          # 3. gera embeddings e indexa
python buscar.py "O que é uma zona de disponibilidade?"   # 4. testa a busca
```

> Conteúdo de origem: Microsoft Learn, sempre citado. O texto coletado não é publicado neste repositório. Projeto de estudo, sem vínculo com a Microsoft.
