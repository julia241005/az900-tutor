# Dockerfile do AZ-900 Tutor para o Hugging Face Spaces (plano gratuito, CPU).
# O servidor baixa o código do GitHub, prepara a base da documentação, baixa o modelo de IA
# e roda tudo junto: a API (FastAPI) e a IA (Ollama). Nenhuma chave de API é necessária.
# Passo a passo: docs/12-publicacao.md

# 1) Pega o programa do Ollama da imagem oficial
FROM ollama/ollama:latest AS ollama

# 2) Ambiente do tutor
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ollama /usr/bin/ollama /usr/bin/ollama
COPY --from=ollama /usr/lib/ollama /usr/lib/ollama

# O Hugging Face roda o container com o usuário de id 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    OLLAMA_MODELS=/home/user/ollama-models \
    OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_KEEP_ALIVE=-1 \
    HF_HOME=/home/user/hf-cache \
    MODO_DEMO=1 \
    LLM_MAX_TOKENS=500 \
    LIMITE_MENSAGENS_POR_MINUTO=6

# Código do projeto (repositório público no GitHub).
# Para pegar uma versão nova do código: Settings do Space > "Factory rebuild".
ARG REPO=https://github.com/julia241005/az900-tutor.git
WORKDIR /home/user
RUN git clone --depth 1 $REPO app
WORKDIR /home/user/app

# Bibliotecas Python (PyTorch na versão só-CPU, bem menor)
RUN pip install --no-cache-dir --user torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --user -r requirements.txt

# Base de conhecimento: baixa as páginas oficiais, divide, indexa e carrega as questões do simulado
RUN python -m ingestao.coletar \
    && python -m ingestao.fragmentar \
    && python -m ingestao.indexar \
    && python importar_perguntas.py

# Modelo de IA (~2 GB), baixado uma vez durante a construção
RUN ollama serve & \
    for i in $(seq 1 60); do ollama list >/dev/null 2>&1 && break; sleep 1; done; \
    ollama pull qwen2.5:3b

COPY --chown=user start.sh /home/user/start.sh
RUN sed -i 's/\r$//' /home/user/start.sh   # remove quebras de linha do Windows, se houver
EXPOSE 7860
CMD ["bash", "/home/user/start.sh"]
