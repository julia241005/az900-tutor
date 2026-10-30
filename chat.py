"""
chat.py — Converse com o agente no terminal.

Rode:  python chat.py
Exemplos:
  - Qual a diferença entre LRS e GRS?
  - E o ZRS?                         (usa a memória da conversa)
  - Me faz um simulado de governança com 2 perguntas
  - B                                (responde o simulado)
  - Como está meu progresso?         (desempenho por área do exame)
Digite "sair" para encerrar.
"""
from openai import APIConnectionError

from agente import ResultadoAgente, conversar_stream
from config import LLM_MODELO

print(f"\n🎓 AZ-900 Tutor (agente) · modelo local: {LLM_MODELO}")
print("Pergunte algo, peça um simulado ou digite 'sair'.\n")

while True:
    try:
        mensagem = input("👤 Você: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not mensagem:
        continue
    if mensagem.lower() in ("sair", "exit", "quit"):
        break

    print("\n🤖 Tutor: ", end="", flush=True)
    try:
        for parte in conversar_stream("terminal", mensagem):
            if isinstance(parte, ResultadoAgente):
                r = parte
            else:
                print(parte, end="", flush=True)
    except APIConnectionError:
        print("não consegui falar com o modelo. O Ollama está aberto? (procure a lhama 🦙 perto do relógio)\n")
        continue

    if r.fontes:
        print("\n\n📚 Fontes:")
        for f in r.fontes:
            print(f"  [{f['numero']}] {f['titulo']} — {f['url']}")
    usadas = ", ".join(r.ferramentas_usadas) or "nenhuma"
    print(f"\n🔧 Ferramentas: {usadas} · 📊 {r.tokens_entrada}+{r.tokens_saida} tokens · ⏱️ {r.segundos}s\n")

print("\nAté a próxima! Bons estudos. 👋")
