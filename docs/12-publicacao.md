# 12 · Publicação

> **Objetivo:** ter um link público para mostrar o projeto, com custo zero.
> **Arquivos no código:** [`docs/index.html`](index.html) (demonstração online), [`deploy/huggingface/`](../deploy/huggingface/) (versão completa), [`roteador.py`](../roteador.py)

## O que está publicado: demonstração no GitHub Pages

**Link:** https://julia241005.github.io/az900-tutor/

| Parte | Online | Por quê |
|---|---|---|
| Página do projeto | ✅ | explica o que é, como funciona, resultados e limitações |
| Simulado | ✅ funciona de verdade | as 30 questões revisadas rodam no navegador, com correção e fonte |
| Meu progresso | ✅ funciona de verdade | calculado no navegador e salvo nele (localStorage) |
| Tirar dúvidas com IA | ❌ só demonstração | a IA precisa de um servidor; mostra um exemplo real de resposta e como rodar localmente |

**Como ativar (uma vez):** no GitHub, **Settings → Pages → Source: Deploy from a branch → Branch: `main` / pasta `/docs` → Save**. Depois de 1 a 2 minutos, o link fica no ar. A cada `git push`, a página se atualiza sozinha.

O arquivo `docs/.nojekyll` faz o GitHub servir os arquivos como estão, sem processar.

## Por que não a versão completa online (decisão registrada)

O plano inicial era publicar o tutor completo (com a IA) no **Hugging Face Spaces**, com o Ollama rodando dentro do servidor. Na hora de criar o Space, o Hugging Face exigia **plano pago para Spaces com Docker ou Gradio**: de graça, só páginas estáticas.

Outras opções gratuitas foram descartadas:

| Opção | Por que não |
|---|---|
| Render, Koyeb | memória insuficiente (cerca de 512 MB) para o modelo de busca e a IA |
| Oracle Cloud (gratuito) | exige cartão de crédito no cadastro e configuração de servidor |
| Expor o computador local na internet | risco de segurança (é um computador de trabalho) |

**Decisão:** publicar a parte que funciona sem servidor (simulado e progresso) e manter a IA local. Os arquivos da versão completa ficam prontos em `deploy/huggingface/`, caso surja uma opção gratuita ou com orçamento.

---

## Versão completa (Hugging Face, plano pago)

## Como funciona

```
GitHub (código público)
      │  git clone durante a construção
      ▼
Hugging Face Space (Docker, CPU gratuita: 2 vCPUs, 16 GB de RAM)
  ├─ instala as bibliotecas Python (PyTorch só-CPU)
  ├─ baixa as páginas oficiais, divide e indexa (a base fica dentro da imagem)
  ├─ baixa o modelo de IA (qwen2.5:3b) para o Ollama
  └─ start.sh: liga o Ollama + a API na porta 7860
```

No Space ficam **só 3 arquivos** (`README.md`, `Dockerfile`, `start.sh`). O código vem do GitHub, então não é preciso enviar o projeto inteiro nem criar token.

## Diferenças da versão online

| | No seu computador | Online (`MODO_DEMO=1`) |
|---|---|---|
| Sessão | sempre a mesma (`web`): o seu progresso | uma por navegador (cada visitante tem a sua) |
| Aviso de demonstração | não | sim |
| Limite de mensagens | 20 por minuto | 6 por minuto, por IP (lido do `X-Forwarded-For`) |
| Tamanho máximo da resposta | 700 tokens | 500 tokens (mais rápido) |
| Histórico e progresso | ficam para sempre | apagados quando o servidor reinicia |

## Passo a passo (Hugging Face)

1. **GitHub:** enviar o código (`git push`) e deixar o repositório **público**.
2. **Hugging Face:** criar uma conta gratuita em https://huggingface.co.
3. **New Space:**
   - Nome: `az900-tutor`
   - License: MIT (ou outra)
   - SDK: **Docker** → template **Blank**
   - Hardware: **CPU basic (free)**
   - Visibilidade: **Public**
4. Na aba **Files** do Space: **Add file → Upload files** e enviar os 3 arquivos da pasta `deploy/huggingface/`. Se perguntar, substituir o `README.md`.
5. Aguardar a construção (**Building**, entre 15 e 30 minutos na primeira vez). Quando aparecer **Running**, o tutor está no ar.

## Atualizar a versão online

Depois de um `git push` com mudanças: no Space, **Settings → Factory rebuild**. O servidor baixa o código de novo e reconstrói.

## Limitações do plano gratuito

- **Lento:** CPU compartilhada, cada resposta pode levar de 30 segundos a 1 minuto.
- **Dorme sem uso:** depois de um tempo sem visitas, o Space pausa e leva alguns minutos para acordar.
- **Sem disco permanente:** histórico e progresso são apagados quando o servidor reinicia.

## Velocidade: roteamento por regras

Antes, cada dúvida chamava a IA **duas vezes**: uma para decidir a ferramenta e outra para responder. Agora o [`roteador.py`](../roteador.py) decide por regras simples (dúvida, simulado, progresso ou conversa), e a IA é chamada **uma vez só**. Conversa simples ("oi", "obrigada") e pedidos de simulado ou progresso não chamam a IA nenhuma vez.

O modo antigo continua disponível com `ROTEAMENTO=llm` no `.env`, útil para comparar ou demonstrar o *tool calling*.
