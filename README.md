# ☁️ AZ-900 Tutor

**Um assistente de estudo com IA para a certificação Microsoft Azure Fundamentals (AZ-900).**
Ele responde dúvidas consultando a documentação oficial da Microsoft, mostra de onde tirou cada informação, aplica simulados e acompanha o seu desempenho por área do exame.

> 💸 **Custo zero.** A IA roda no seu próprio computador. Nenhuma API paga, nenhuma assinatura.

---

## Em 30 segundos

Você pergunta *"Qual a diferença entre ZRS e GRS?"*. Antes de responder, o tutor **procura nas páginas oficiais da Microsoft** os trechos que falam disso, **lê esses trechos** e explica em português, citando as fontes `[1]`, `[2]` com o link para conferir.

Se ele não encontrar a resposta na documentação, ele **diz que não encontrou**, em vez de inventar.

---

## Por que eu fiz

Eu estava estudando para o AZ-900 e senti falta de duas coisas:

1. **Respostas confiáveis.** Chats de IA genéricos às vezes respondem com segurança algo que está errado ou desatualizado. Para estudar para uma prova, preciso saber **de onde veio** a informação.
2. **Saber onde estou fraca.** O simulado oficial dá uma nota, mas eu queria acompanhar a evolução por área do exame e saber o que revisar.

Ao mesmo tempo, eu queria aprender na prática como se constrói um produto com IA de verdade: alimentar a IA com dados, fazer ela buscar informação, medir se ela acerta e quanto custa.

---

## O que ele faz

| Função | Como funciona |
|---|---|
| 💬 **Tirar dúvidas** | Responde com base na documentação oficial, sempre com as fontes. Entende continuação ("e o ZRS?") |
| 📝 **Simulado** | Questões por área do exame, correção na hora, explicação e link oficial. Dá para responder pelo teclado (A, B, C, D) |
| 📊 **Meu progresso** | Desempenho por área, com os pesos oficiais do exame, e recomendação do que estudar |
| 🔁 **Lembra a conversa** | O histórico fica salvo, mesmo depois de fechar |
| 🚫 **Recusa o que não sabe** | Perguntas fora do AZ-900 ou sem resposta na documentação são recusadas |

---

## O que ele **não** faz (limitações)

Prefiro ser transparente. Estes são os pontos fracos conhecidos:

| Limitação | Por quê |
|---|---|
| **Só AZ-900** | Ele foi feito para responder só sobre essa prova. Outros assuntos são recusados de propósito |
| **É lento** | A IA roda no processador, sem placa de vídeo. Na medição, uma resposta levava em média **24 segundos** (já reduzi as chamadas à IA de 2 para 1 por pergunta). Na versão online gratuita, pode levar até 1 minuto. O simulado e o progresso são instantâneos, porque não usam IA |
| **Erra às vezes** | O modelo é pequeno (3 bilhões de parâmetros) para caber num computador comum. Na avaliação, ele trouxe a fonte certa em 97% das perguntas, mas em alguns casos leu errado o trecho. Por isso as fontes estão sempre visíveis: confira |
| **Banco de questões pequeno** | São 30 questões revisadas por mim, com fonte oficial. A IA até consegue gerar questões, mas nos testes nenhuma passou na minha revisão, então essa função fica desligada |
| **Conteúdo é uma "foto"** | A documentação foi baixada numa data. Quando a Microsoft muda algo, é preciso rodar a atualização (`atualizar_base.py`) |
| **Sem contas de usuário** | No computador, é feito para uma pessoa. Na versão online, cada navegador tem o próprio histórico, mas ele é apagado quando o servidor reinicia |
| **Não substitui a prova oficial** | É material de apoio. Use também os simulados oficiais do Microsoft Learn |

---

## Como funciona (explicado de forma simples)

Imagine um professor que, antes de responder qualquer pergunta, **abre a apostila oficial, procura as páginas certas e lê**. É isso que o tutor faz. Essa técnica se chama **RAG** (geração aumentada por recuperação).

```
1. PREPARAR (feito uma vez)
   Páginas oficiais do Microsoft Learn ──► texto limpo ──► pedaços de ~1.200 letras
   ──► cada pedaço vira uma "impressão digital" numérica (embedding) ──► guardado num banco

2. RESPONDER (a cada pergunta)
   Sua pergunta ──► busca os 4 trechos mais parecidos (pelo significado E pela palavra exata)
                ──► a IA lê só esses trechos ──► responde citando [1] [2] [3]
```

**Por que buscar pelo significado *e* pela palavra exata?** A busca por significado entende sinônimos, mas se confunde com siglas como LRS, GRS e ZRS. A busca por palavra exata resolve isso. Juntando as duas, a fonte certa passou a vir em **97%** das perguntas (antes, 93%).

**E o simulado?** Ele **não usa IA**: as questões vêm de um banco revisado e a correção é feita por código. Por isso é instantâneo e nunca erra o gabarito.

---

## Tecnologias (e por que cada uma)

| O quê | Tecnologia | Por que essa |
|---|---|---|
| Linguagem | **Python** | a linguagem mais usada em IA |
| IA que escreve as respostas | **Ollama + Qwen 2.5 (3B)** | roda no próprio computador, de graça |
| "Impressão digital" do texto | **sentence-transformers** (modelo multilíngue) | entende português e roda localmente |
| Banco de busca | **ChromaDB** | banco vetorial simples, num arquivo |
| Busca por palavra exata | **BM25** (feito no projeto) | resolve siglas como LRS, GRS |
| API | **FastAPI** | rápida e já gera a documentação da API |
| Interface | **HTML, CSS e JavaScript** | leve, servida pela própria API, sem instalar nada a mais |
| Histórico e progresso | **SQLite** | banco de dados num arquivo, já vem com o Python |
| Testes | **pytest** | 42 testes automáticos |

---

## Resultados medidos

Eu não queria dizer só "funciona". Criei um conjunto de **30 perguntas do exame + 3 fora do assunto** e medi ([detalhes](docs/09-avaliacao.md)):

| O que foi medido | Resultado |
|---|---|
| A fonte certa veio entre os trechos (busca híbrida) | **97%** |
| A fonte certa veio em 1º lugar com mais frequência (MRR) | 0,80 → **0,90** |
| Recusou perguntas fora do assunto (bolo, futebol) | **100%** |
| Fonte certa entre as citadas na resposta | **97%** |
| Tempo médio por resposta | 24 s |
| Custo real | **US$ 0,00** |

A avaliação também mostrou um problema: em **13%** das perguntas ele dizia "não encontrei" mesmo com a resposta nos trechos, principalmente em comparações (ex.: LRS x GRS). Ajustei as instruções da IA para juntar informações de trechos diferentes. Esse ciclo de **medir → achar a causa → ajustar → medir de novo** está documentado no [doc 09](docs/09-avaliacao.md).

---

## Como usar

### O que você precisa

- **Python 3.10** ou mais novo
- **[Ollama](https://ollama.com)** instalado
- **Git**
- Uns 3 GB livres (modelo de IA + documentação)

### Instalação (uma vez só)

```bash
git clone https://github.com/julia241005/az900-tutor.git
cd az900-tutor

python -m venv venv
source venv/Scripts/activate        # Git Bash no Windows (no Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

ollama pull qwen2.5:3b              # baixa o modelo de IA (~2 GB)

python -m ingestao.coletar          # baixa as páginas oficiais
python -m ingestao.fragmentar       # divide em pedaços
python -m ingestao.indexar          # cria o banco de busca
python importar_perguntas.py        # carrega as questões do simulado
```

### Dia a dia

1. Abra o **Ollama**.
2. Dê dois cliques em **`Iniciar AZ-900 Tutor.bat`** (Windows), ou rode `python -m uvicorn api:app --port 8000`.
3. Acesse **http://127.0.0.1:8000** e use as abas **Tirar dúvidas**, **Simulado** e **Meu progresso**.

### Comandos úteis

```bash
python -m pytest -q          # roda os testes automáticos
python avaliar.py            # mede a qualidade da busca
python avaliar.py --completo # mede a qualidade das respostas (Ollama aberto, ~15 min)
python relatorio.py          # uso, tempo, tokens e quanto custaria numa API paga
python atualizar_base.py     # baixa a documentação de novo e reindexa se algo mudou
```

---

## Estrutura do projeto

```
az900-tutor/
├── ingestao/              ← baixa, limpa, divide e indexa a documentação
├── buscar.py              ← busca híbrida (significado + palavra exata)
├── rag.py                 ← monta a resposta com as fontes
├── roteador.py            ← decide o que fazer: dúvida, simulado, progresso ou conversa
├── agente.py              ← executa a decisão e conversa com o aluno
├── api.py                 ← API (FastAPI) e interface
├── web/index.html         ← interface
├── banco.py · sessao.py   ← histórico, progresso e banco de questões (SQLite)
├── avaliar.py             ← avaliação automática
├── relatorio.py           ← uso e custo
├── tests/                 ← testes automáticos
├── deploy/huggingface/    ← arquivos para publicar de graça no Hugging Face
├── docs/                  ← documentação de cada etapa (01 a 12)
└── avaliacao/             ← perguntas de teste e resultados
```

---

## Documentação de cada etapa

| # | Etapa |
|---|---|
| 01 | [Fontes de dados](docs/01-fontes-de-dados.md) |
| 02 | [Ingestão e limpeza](docs/02-ingestao-e-limpeza.md) |
| 03 | [Fragmentação (chunking)](docs/03-fragmentacao.md) |
| 04 | [Embeddings, indexação e busca híbrida](docs/04-embeddings-e-indexacao.md) |
| 05 | [Recuperação e RAG](docs/05-recuperacao-e-rag.md) |
| 06 | [Agente e ferramentas](docs/06-agente-e-ferramentas.md) |
| 07 | [Progresso e banco de perguntas](docs/07-progresso-e-banco-de-perguntas.md) |
| 08 | [Atualização da base](docs/08-atualizacao.md) |
| 09 | [Avaliação de qualidade](docs/09-avaliacao.md) |
| 10 | [Custo, tokens e observabilidade](docs/10-custo.md) |
| 11 | [Segurança e ética](docs/11-seguranca-e-etica.md) |
| 12 | [Publicação gratuita (Hugging Face)](docs/12-publicacao.md) |

O passo a passo completo do desenvolvimento está no [ROADMAP](ROADMAP.md).

---

## Próximos passos

- [x] Respostas mais rápidas: a IA passou a ser chamada 1 vez por pergunta, em vez de 2
- [x] Versão online gratuita no Hugging Face ([como foi publicado](docs/12-publicacao.md))
- [ ] **Modo prova real:** cronômetro e nota só no final, como no dia do exame
- [ ] **Revisar meus erros:** refazer só as questões erradas até acertar
- [ ] Flashcards com repetição espaçada
- [ ] Outras certificações (AZ-104, AI-900) usando a mesma estrutura
- [ ] Demonstração em vídeo

---

## Aviso

Projeto pessoal de estudo, **sem vínculo com a Microsoft**. O conteúdo vem do [Microsoft Learn](https://learn.microsoft.com) e é sempre citado com link. O texto baixado **não é publicado** neste repositório: cada pessoa baixa a própria cópia com o passo de instalação.

Feito por **Julia Duarte Silva**.
