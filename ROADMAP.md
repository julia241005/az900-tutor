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
- [x] Testar no terminal (`python rag.py`) e na API (`http://localhost:8000/docs`)
- [x] Documentar: `docs/05-recuperacao-e-rag.md`
- [x] Commit + tag `fase-2`

**Conceitos:** RAG, prompt de sistema, guardrails, contexto, tokens, streaming, API REST.

---

## Fase 3 · Agente com ferramentas (≈ 1–2 semanas)
**Objetivo:** o tutor deixa de só responder e passa a **decidir o que fazer**.

- [x] Ferramenta `buscar_documentacao` (nossa base local)
- [x] Ferramenta `gerar_simulado` (perguntas por área, JSON validado, alternativas embaralhadas)
- [x] Correção determinística `corrigir_resposta` (código, sem IA)
- [x] Ciclo do agente: pergunta → LLM escolhe a ferramenta → executa → responde
- [x] Guardrail: dúvida sem busca é redirecionada ao RAG
- [x] Histórico da conversa (memória de curto prazo)
- [x] Endpoints `/chat` e `/chat/stream` na API
- [x] Chat no terminal (`python chat.py`)
- [x] Documentar: `docs/06-agente-e-ferramentas.md`
- [x] Testar com perguntas variadas
- [ ] (Extra) Ferramenta `buscar_microsoft_learn` via servidor MCP oficial
- [x] Commit + tag `fase-3`

**Conceitos:** agentes, tool use / function calling, MCP, memória de conversa.

---

## Fase 4 · Simulado e progresso (≈ 1–2 semanas)
**Objetivo:** acompanhar o aluno como o relatório oficial da Microsoft, só que melhor.

- [x] Banco de dados SQLite: respostas, acertos, área e data (`banco.py`)
- [x] **Banco de perguntas com revisão humana:** a IA gera, você aprova (`revisar_perguntas.py`)
- [x] Geração em lote para o banco (`gerar_banco.py`)
- [x] Simulado usa primeiro as perguntas aprovadas (mais rápido e confiável)
- [x] Desempenho por área com os pesos oficiais do exame (`progresso.py`)
- [x] Recomendação de estudo + páginas para revisar
- [x] Ferramenta `ver_progresso` no agente ("como está meu progresso?")
- [x] Endpoints `/progresso/{sessao_id}` e `/banco/resumo`
- [x] Mensagem clara quando o Ollama está fechado (chat e API)
- [x] Documentar: `docs/07-progresso-e-banco-de-perguntas.md`
- [x] Gerar e revisar as primeiras perguntas do banco (0 de 11 aprovadas → estratégia revista)
- [x] Banco curado de 30 perguntas com fonte oficial (`importar_perguntas.py`)
- [x] Simulado usa só perguntas aprovadas; geração por IA vira opcional
- [ ] (Extra) Adicionar seus flashcards e "pegadinhas" como fonte própria
- [x] Commit + tag `fase-4`

**Conceitos:** memória de longo prazo, human-in-the-loop, dados estruturados + IA.

---

## Fase 5 · Interface (v1 concluída)
**Objetivo:** usar o tutor pelo navegador, sem terminal.

- [x] Interface web servida pela própria API (`web/index.html`, sem instalar nada novo)
- [x] Aba Tirar dúvidas: chat com streaming, fontes oficiais, tokens e tempo
- [x] Aba Simulado: perguntas aprovadas do banco, correção instantânea com explicação e fonte
- [x] Aba Meu progresso: desempenho por área com pesos oficiais e recomendação
- [x] Tema claro/escuro automático e layout para celular
- [x] Atalho `Iniciar AZ-900 Tutor.bat` (liga a API e abre o navegador)
- [x] Endpoints `/simulado/perguntas` e `/simulado/responder` (sem IA, instantâneos)
- [ ] Prints da interface na pasta `docs/imagens/` para o README
- [ ] (v2, opcional) Migrar para Next.js + Tailwind + shadcn/ui, reaproveitando a mesma API

**Conceitos:** frontend consumindo API REST, streaming (SSE) no navegador, UX de produtos de IA.

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
- [ ] Documentar: `docs/08-atualizacao.md`, `docs/09-avaliacao.md`, `docs/10-custo.md`
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
- [ ] Documentar: `docs/11-seguranca-e-etica.md`
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
├── docs/               ← processos 01–11 + imagens
├── avaliacao/          ← perguntas de teste e resultados
├── README.md
└── ROADMAP.md          ← este arquivo
```
