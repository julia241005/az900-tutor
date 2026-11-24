# 13 · Várias certificações (multi-trilha)

O tutor nasceu focado no **AZ-900**. Esta etapa o transformou numa plataforma
**multi-certificação**: o usuário escolhe a certificação ("trilha") e tudo passa a
responder, simular e medir progresso **daquela** certificação — sem misturar os dados.

## A ideia central: a "trilha"

Uma **trilha** é o perfil de uma certificação. Fica no catálogo `trilhas.py`:

```
Trilha(
  id="aws-clf-c02", sigla="CLF-C02", titulo="AWS Certified Cloud Practitioner",
  provedor="Amazon Web Services", foco="Infraestrutura / Nuvem", inicial="W", cor="#ff9900",
  colecao="aws_clf_c02", perguntas_arquivo="perguntas/aws-clf-c02.json",
  areas=(Area("Segurança e Conformidade", 30, "30%", ("iam","mfa",...)), ...),
  fontes=(...URLs oficiais...),
)
```

Cada trilha guarda: as **áreas do exame** (com pesos e palavras-chave), as **fontes
oficiais** da documentação, o **banco de perguntas** e uma **coleção de vetores** própria.

## Como a trilha percorre o sistema

A trilha escolhida é a **fonte da verdade** da conversa. Ela é guardada na `Sessao`
(`sessao.trilha`) e passada por toda a cadeia, sempre como parâmetro **opcional com
padrão** (então o código e os testes antigos continuam funcionando):

```
interface  →  /chat/stream {trilha}  →  Sessao.trilha
                                           ├─ rag.responder_stream(pergunta, trilha)   → prompt + coleção da trilha
                                           ├─ roteador.decidir(msg, trilha)            → áreas da trilha
                                           ├─ simulado.obter_perguntas(sessao)         → banco da trilha
                                           └─ progresso.calcular(sessao_id, trilha)    → pesos da trilha
```

## Isolamento dos dados (por trilha)

Cada certificação tem a sua própria pasta em `data/<id>/`:

```
data/az900/        vetores/  fragmentos.jsonl  tutor.db  brutos/
data/aws-clf-c02/  vetores/  fragmentos.jsonl  tutor.db  brutos/
```

Assim o progresso do AZ-900 nunca se mistura com o da AWS, e cada busca acontece na
coleção de vetores certa. Na interface, a sessão também é separada por trilha
(`web::az900`, `web::aws-clf-c02`).

## O que muda na interface

A lateral ganhou um **seletor de certificação** (agrupado por área de foco: Infra,
Redes, DevOps, Segurança). Ao trocar, a marca, as áreas e a sessão mudam, e cada
requisição leva o `trilha` escolhido. O catálogo vem do endpoint `GET /trilhas`.

## Adicionar uma nova certificação

1. Adicione uma `Trilha` no `trilhas.py` (áreas, pesos, palavras e fontes oficiais).
2. Crie `perguntas/<id>.json` com algumas perguntas curadas (modelo: `perguntas/curadas.json`).
3. Rode a ingestão só daquela trilha:
   ```
   python -m ingestao.coletar    --trilha <id>
   python -m ingestao.fragmentar --trilha <id>
   python -m ingestao.indexar    --trilha <id>
   python importar_perguntas.py  --trilha <id>
   ```

Nenhum outro arquivo precisa mudar: o catálogo é o único ponto de configuração.

## Compatibilidade

- Todos os parâmetros `trilha` têm **padrão** (`az900`), então os 42 testes continuam válidos.
- O layout antigo (`data/vetores`, `data/tutor.db`...) é migrado para `data/az900/` com
  `python migrar_dados.py` — **sem precisar reindexar** o AZ-900.
