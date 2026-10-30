# 01 · Fontes de dados

> **Objetivo:** definir de onde vem o conhecimento do tutor, por que cada fonte foi escolhida e o que **não** é usado.
> **Arquivo no código:** [`ingestao/fontes.py`](../ingestao/fontes.py)

## Princípio

O tutor só responde com base em **fontes oficiais e rastreáveis**. Toda resposta precisa poder apontar de onde veio a informação (URL). Isso reduz alucinação e dá confiança ao aluno.

## Camadas de fontes

| Camada | Fonte | Tipo no código | Função | Status |
|---|---|---|---|---|
| 1 · Oficial | Guia de estudo AZ-900 (Skills measured) | `guia` | Esqueleto do exame: áreas e pesos | ✅ Fase 1 |
| 1 · Oficial | Trilha de treinamento AZ-900 (12 módulos) | `treinamento` | Conteúdo didático, no nível do exame | ✅ Fase 1 |
| 1 · Oficial | Documentação técnica do Azure (28 páginas) | `documentacao` | Aprofundamento e detalhes técnicos | ✅ Fase 1 |
| 1 · Oficial | Servidor MCP do Microsoft Learn | — | Busca ao vivo quando a base local não tiver a resposta | ⏳ Fase 3 |
| 2 · Próprio | Anotações, flashcards e "pegadinhas" | `proprio` | Explicações simples em português | ⏳ Fase 4 |
| 3 · Gerado + revisado | Banco de perguntas de simulado | `simulado` | Perguntas geradas pela IA e **aprovadas por humano** | ⏳ Fase 4 |

## Organização por área do exame

Cada fonte recebe uma das áreas oficiais do AZ-900, usada como **metadado** para filtrar buscas e medir desempenho:

- Conceitos de nuvem
- Arquitetura e serviços do Azure
- Gestão e governança do Azure
- Geral (guia de estudo)

## Licença e uso

| Fonte | Observação |
|---|---|
| Documentação do Azure | Publicada pela Microsoft com licença aberta (CC BY 4.0 no repositório público da documentação). Uso permitido com atribuição: o tutor sempre cita a URL. |
| Trilha de treinamento | Conteúdo da Microsoft. Usado apenas como base de consulta local, com citação e link para o original. **O texto coletado não é publicado** neste repositório (`data/` está no `.gitignore`). |

## O que NÃO é usado (e por quê)

| Fonte | Motivo |
|---|---|
| Dumps / perguntas "vazadas" do exame | Violam o contrato do exame da Microsoft |
| Conteúdo de cursos pagos (Alura, Udemy etc.) | Direitos autorais |
| Blogs e fóruns não oficiais | Risco de informação desatualizada ou incorreta |

## Como adicionar uma fonte

1. Adicione um item em `FONTES` (`ingestao/fontes.py`) com `tipo`, `area` e `url`.
2. Rode o pipeline novamente (`coletar` → `fragmentar` → `indexar`).
3. Registre a mudança neste documento.
