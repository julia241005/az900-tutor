# 12 · Publicação (Hugging Face Spaces, grátis)

> **Objetivo:** colocar o tutor no ar, de graça, sem nenhuma chave de API.
> **Arquivos no código:** [`deploy/huggingface/`](../deploy/huggingface/), [`roteador.py`](../roteador.py)

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

## Passo a passo

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
