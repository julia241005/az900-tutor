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
import argparse

from openai import APIConnectionError

import sessao as sessao_mod
import trilhas
from agente import ResultadoAgente, conversar_stream
from config import LLM_MODELO, TRILHA_PADRAO

ap = argparse.ArgumentParser(description="Converse com o tutor no terminal.")
ap.add_argument("--trilha", default=TRILHA_PADRAO, help="certificação a estudar (ex.: az900, aws-clf-c02).")
_args = ap.parse_args()
TRILHA = _args.trilha if trilhas.existe(_args.trilha) else TRILHA_PADRAO
t = trilhas.obter(TRILHA)
sessao_mod.obter_sessao("terminal", TRILHA)  # fixa a trilha desta conversa de terminal

print(f"\n🎓 {t.sigla} Tutor (agente) · {t.titulo} · modelo local: {LLM_MODELO}")
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
