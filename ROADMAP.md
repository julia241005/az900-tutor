# 🗺️ Roadmap — AZ-900 Tutor

Passo a passo do início ao fim do projeto. Marque `[x]` conforme avançar.
Ao final de **cada fase**: `git add .` → `git commit -m "..."` → `git tag fase-N` → `git push --tags`

**Duração estimada:** 8 a 10 semanas, com algumas horas por semana.
**Custo:** zero. LLM local (Ollama), embeddings locais e hospedagem em planos gratuitos.

---

## ✅ Fase 1 · Alimentação (concluída)
- [x] Ambiente: Python, VS Code, venv, dependências
- [x] Coletar páginas oficiais do Microsoft Learn (105 páginas)
- [x] Limpar HTML, corrigir codificação (UTF-8), remover ruídos
- [x] Fragmentar (chunking com sobreposição e metadados)
- [x] Gerar embeddings e indexar no ChromaDB
- [x] Testar a busca semântica
- [x] Documentar processos 01–04
- [x] **Git:** commit e tag `fase-1`

**Conceitos:** ingestão de dados, chunking, embeddings, banco vetorial, busca semântica.

---

## Fase 2 · RAG + API (≈ 1–2 semanas)
**Objetivo:** o LLM lê os trechos encontrados e responde em português, como um professor, citando as fontes.

- [x] Instalar o Ollama e o modelo `qwen2.5:3b` (LLM local, **custo zero**)
- [x] `rag.py`: pergunta → busca trechos → filtro de relevância → monta o prompt → LLM → resposta
- [x] **Prompt de sistema:** papel de tutor, responder só com base nos trechos, dizer "não sei" quando não houver fonte
- [x] Citação de fontes na resposta (título + link)
- [x] Mostrar tokens e tempo de cada resposta
- [x] **Streaming:** a resposta aparece aos poucos
- [x] **API com FastAPI:** `/saude`, `/perguntar`, `/perguntar/stream`
- [ ] Testar no terminal (`python rag.py`) e na API (`http://localhost:8000/docs`)
- [x] Documentar: `docs/05-recuperacao-e-rag.md`
- [ ] Commit + tag `fase-2`

**Conceitos:** RAG, prompt de sistema, guardrails, contexto, tokens, streaming, API REST.

---

## Fase 3 · Agente com ferramentas (≈ 1–2 semanas)
**Objetivo:** o tutor deixa de só responder e passa a **decidir o que fazer**.

- [ ] Ferramenta `buscar_documentacao` (nossa base local)
- [ ] Ferramenta `buscar_microsoft_learn` (servidor MCP oficial, busca ao vivo)
- [ ] Ferramenta `gerar_simulado` (perguntas por área do exame)
- [ ] Ferramenta `corrigir_resposta` (corrige e explica o erro)
- [ ] Ciclo do agente: pergunta → LLM escolhe a ferramenta → executa → responde
- [ ] Histórico da conversa (memória de curto prazo)
- [ ] Endpoint `/chat` na API
- [ ] Testar com perguntas variadas e registrar exemplos
- [ ] Commit + tag `fase-3`

**Conceitos:** agentes, tool use / function calling, MCP, memória de conversa.

---

## Fase 4 · Simulado e progresso (≈ 1–2 semanas)
**Objetivo:** acompanhar o aluno como o relatório oficial da Microsoft, só que melhor.

- [ ] Banco de dados SQLite: respostas, acertos, área e data
- [ ] **Banco de perguntas com revisão humana:** a IA gera, você aprova (script `revisar_perguntas.py`)
- [ ] Cálculo do desempenho por área do exame
- [ ] Ferramenta `recomendar_estudo` (o que revisar, com links)
- [ ] Endpoints `/simulado` e `/progresso`
- [ ] Adicionar seus flashcards e "pegadinhas" como fonte própria
- [ ] Documentar: `docs/06-banco-de-perguntas.md`
- [ ] Commit + tag `fase-4`

**Conceitos:** memória de longo prazo, human-in-the-loop, dados estruturados + IA.

---

## Fase 5 · Interface moderna (≈ 2–3 semanas)
**Objetivo:** visual de produto real, elegante e responsivo.

- [ ] Protótipo visual das 3 telas (aprovar o design antes de programar)
- [ ] Instalar Node.js
- [ ] Criar o app Next.js na pasta `frontend/`
- [ ] Configurar Tailwind CSS + shadcn/ui + Framer Motion
- [ ] Identidade visual: dark mode, paleta azul/violeta, tipografia Inter/Geist
- [ ] **Tela Chat:** streaming, cards de fonte, etiqueta da área, sugestões de perguntas
- [ ] **Tela Simulado:** cartões, barra de progresso, feedback animado
- [ ] **Tela Painel:** desempenho por área, evolução, card "Estude agora"
- [ ] Conectar o frontend à API
- [ ] Responsivo (celular) + tema claro/escuro
- [ ] Prints e GIF na pasta `docs/imagens/`
- [ ] Commit + tag `fase-5`

**Conceitos:** frontend moderno, TypeScript, integração com API, UX de produtos de IA.

---

## Fase 6 · Qualidade e custo (≈ 1 semana)
**Objetivo:** provar que o tutor acerta e saber quanto ele custa.

- [ ] Conjunto de avaliação: 30 perguntas com resposta esperada e fonte correta
- [ ] Métrica de busca: a fonte certa veio entre os trechos?
- [ ] Métrica de resposta: a resposta é fiel aos trechos? (LLM como avaliador)
- [ ] Ajustar chunking, `TOP_K` e prompt com base nos resultados
- [ ] Registrar tokens e custo de cada pergunta
- [ ] Relatório de custo: custo médio por pergunta e por aluno (FinOps de IA)
- [ ] Rotina de atualização da base (recoletar e reindexar)
- [ ] Documentar: `docs/07-atualizacao.md`, `docs/08-avaliacao.md`, `docs/09-custo.md`
- [ ] Commit + tag `fase-6`

**Conceitos:** evals, LLM-as-judge, observabilidade, unit economics de IA.

---

## Fase 7 · Publicação (≈ 1 semana)
**Objetivo:** projeto no ar, com link para mostrar.

- [ ] Dockerfile do backend
- [ ] Deploy do backend em plano gratuito (ex.: Hugging Face Spaces ou Render)
- [ ] Deploy do frontend em plano gratuito (Vercel)
- [ ] LLM da versão online: provedor com plano gratuito ou demo em vídeo usando o Ollama local
- [ ] Variáveis de ambiente e segredos (nunca no código)
- [ ] Proteções: limite de perguntas por usuário
- [ ] Documentar: `docs/10-seguranca-e-etica.md`
- [ ] README final: demo, GIF, arquitetura, resultados da avaliação e custo
- [ ] Tornar o repositório público
- [ ] Post no LinkedIn contando a jornada
- [ ] Tag `v1.0` 🎉

**Conceitos:** containers, deploy, segredos, controle de custos em produção.

---

## Estrutura final do repositório

```
az900-tutor/
├── ingestao/           ← Python: pipeline de alimentação
├── rag.py · api.py     ← Python: RAG, agente e API (FastAPI)
├── frontend/           ← Next.js: chat, simulado, painel
├── docs/               ← processos 01–10 + imagens
├── avaliacao/          ← perguntas de teste e resultados
├── README.md
└── ROADMAP.md          ← este arquivo
```
