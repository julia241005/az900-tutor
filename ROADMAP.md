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

## ✅ Fase 6 · Qualidade e custo (concluída)
**Objetivo:** provar que o tutor acerta e saber quanto ele custa.

- [x] Conjunto de avaliação: 30 perguntas com fonte e termos esperados + 3 fora do escopo (`avaliacao/conjunto.json`)
- [x] Métrica de busca: acerto@4 e MRR, vetorial × híbrida (`python avaliar.py`)
- [x] Busca híbrida (embeddings + BM25 + RRF): acerto@4 93% → 97%, MRR 0,80 → 0,90
- [x] Métrica de resposta: termos esperados, citação, fonte certa, recusa fora do escopo (`--completo`)
- [x] LLM como avaliador da fidelidade (`--juiz`, indicativo com modelo pequeno)
- [x] Testes automáticos com pytest (27 testes, sem precisar do Ollama)
- [x] Registro de cada interação em JSONL (observabilidade)
- [x] Relatório de uso e custo: tempo médio e p95, tokens, custo por pergunta e por aluno (`relatorio.py`)
- [x] Histórico do chat salvo no SQLite + botão "Nova conversa"
- [x] Status da IA na interface (Ollama ligado ou desligado)
- [x] Rotina de atualização da base com detecção de mudanças (`atualizar_base.py`)
- [x] Documentar: `docs/08-atualizacao.md`, `docs/09-avaliacao.md`, `docs/10-custo.md`
- [ ] Commit + tag `fase-6`

**Conceitos:** evals, busca híbrida, LLM-as-judge, testes, observabilidade, unit economics de IA.

---

## Fase 7 · Publicação
**Objetivo:** projeto no ar, com link para mostrar. Custo zero.

- [x] Respostas mais rápidas: roteamento por regras, 1 chamada à IA por pergunta (`roteador.py`)
- [x] Sessão por navegador na versão online (`MODO_DEMO=1`)
- [x] Dockerfile para o Hugging Face Spaces com Ollama dentro (`deploy/huggingface/`)
- [x] Variáveis de ambiente e segredos (nunca no código): `.env.example`
- [x] Proteções: senha opcional e limite de mensagens por minuto (`seguranca.py`)
- [x] Documentar: `docs/11-seguranca-e-etica.md`, `docs/12-publicacao.md`
- [x] README reescrito: o que faz, o que não faz, como funciona e resultados
- [ ] Repositório público no GitHub
- [ ] Space criado no Hugging Face e funcionando
- [ ] Prints e vídeo curto da interface
- [ ] Post no LinkedIn contando a jornada
- [ ] Tag `v1.0` 🎉

**Conceitos:** containers, deploy, segredos, controle de custos em produção.

---

## Estrutura final do repositório

```
az900-tutor/
├── ingestao/           ← Python: pipeline de alimentação
├── rag.py · api.py     ← Python: RAG, agente e API (FastAPI)
├── web/                ← interface (HTML, CSS e JavaScript)
├── deploy/             ← publicação gratuita (Hugging Face)
├── docs/               ← processos 01–11 + imagens
├── avaliacao/          ← perguntas de teste e resultados
├── tests/              ← testes automáticos (pytest)
├── README.md
└── ROADMAP.md          ← este arquivo
```
