#!/bin/bash
# Inicia a IA (Ollama) e, quando ela estiver pronta, a API do tutor na porta 7860 (padrão do Hugging Face).

ollama serve &

for i in $(seq 1 60); do
  ollama list >/dev/null 2>&1 && break
  sleep 1
done

# "Aquece" o modelo em segundo plano: carrega na memória para a primeira pergunta não demorar mais
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model": "qwen2.5:3b", "prompt": "oi", "stream": false}' >/dev/null &

exec python -m uvicorn api:app --host 0.0.0.0 --port 7860
