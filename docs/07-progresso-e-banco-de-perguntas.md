# 07 · Progresso e banco de perguntas

> **Objetivo:** medir o desempenho do aluno por área do exame e manter um banco de perguntas **revisado por humano**.
> **Arquivos no código:** [`banco.py`](../banco.py), [`progresso.py`](../progresso.py), [`simulado.py`](../simulado.py), [`gerar_banco.py`](../gerar_banco.py), [`revisar_perguntas.py`](../revisar_perguntas.py)

## Memória de curto × longo prazo

| | Curto prazo | Longo prazo |
|---|---|---|
| O quê | Histórico da conversa, simulado em andamento | Respostas do aluno, banco de perguntas |
| Onde | Memória do programa (`sessao.py`) | **SQLite** (`data/tutor.db`) |
| Dura | Até reiniciar | Para sempre |

SQLite foi escolhido por ser um banco de dados completo **em um único arquivo**, que já vem com o Python: zero instalação, zero custo.

## Banco de dados

```
respostas                          perguntas
─────────                          ─────────
sessao_id                          area
area                               enunciado (único)
enunciado                          alternativas (JSON)
correta (1/0)                      correta · explicacao
fonte_titulo · fonte_url           fonte_titulo · fonte_url
respondida_em                      status: pendente | aprovada | rejeitada
```

## Banco de perguntas com revisão humana (human-in-the-loop)

```
IA gera pergunta ──► status "pendente" ──► humano revisa ──► "aprovada"  → reutilizada nos simulados
                     (já pode aparecer,                    └► "rejeitada" → nunca mais aparece
                      com o selo 🧪)
```

- **Por quê:** modelos de IA (principalmente pequenos) podem gerar perguntas ambíguas ou com gabarito errado. Em material de estudo, um erro ensina errado.
- **Revisão:** `python revisar_perguntas.py` mostra pergunta, gabarito, explicação e fonte oficial. Critérios: clareza, só uma alternativa correta, explicação coerente com a fonte.
- **Geração em lote:** `python gerar_banco.py 5` gera 5 perguntas por área para revisar depois.

### Caso real: bug encontrado pela revisão humana
Na primeira revisão, uma pergunta tinha o gabarito certo (**D**), mas a explicação dizia *"A opção **B** é a mais adequada"*.
**Causa:** o código embaralha as alternativas para evitar viés de posição, mas a explicação gerada pela IA continuava citando a letra **antiga**.
**Correção:** (1) o prompt passou a pedir explicações sem citar letras; (2) o código atualiza automaticamente qualquer letra citada na explicação para a nova posição.
Esse caso mostra por que a revisão humana existe: o erro só foi percebido por uma pessoa conferindo a pergunta.

## Simulado: banco primeiro, IA depois

1. Busca perguntas **aprovadas** da área, evitando as que o aluno já respondeu.
2. Só o que faltar é gerado pela IA (e salvo como pendente).

**Benefícios:** simulados muito mais rápidos (sem chamar o LLM), mais confiáveis (revisados) e com menos processamento, o que equivale a custo menor numa API paga.

## Progresso por área

Usa as **3 áreas oficiais e seus pesos** no exame (guia de estudo AZ-900):

| Área | Peso no exame |
|---|---|
| Conceitos de nuvem | 25–30% |
| Arquitetura e serviços do Azure | 35–40% |
| Gestão e governança do Azure | 30–35% |

Para cada área: respostas, acertos, percentual e situação:

| Situação | Regra |
|---|---|
| ▫️ sem dados | nenhuma resposta |
| 🔸 poucos dados | menos de 3 respostas (resultado ainda não confiável) |
| ⚠️ reforçar | abaixo da meta de **80%** (recomendada pela Microsoft nos simulados oficiais) |
| ✅ pronto | 80% ou mais |

A lista **"Revisar"** mostra as páginas oficiais ligadas às perguntas que o aluno errou.

## Recomendação de estudo

Regras simples e explicáveis, em ordem:
1. Sem dados em nenhuma área → começar pela de **maior peso** (Arquitetura).
2. Área com poucos dados → praticar essa área.
3. Pior área abaixo da meta → reforçar essa área, começando pela página mais errada.
4. Tudo acima de 80% → simulados completos e agendar a prova.

## Acesso

| Onde | Como |
|---|---|
| Chat | "Como está meu progresso?" (ferramenta `ver_progresso`) |
| Terminal | `python progresso.py` |
| API | `GET /progresso/{sessao_id}` e `GET /banco/resumo` |

## Privacidade
O banco fica **só no computador local** (`data/` está no `.gitignore`). Nenhuma resposta do aluno é enviada para fora.
