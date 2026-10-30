# 02 · Ingestão e limpeza

> **Objetivo:** transformar páginas web em texto limpo, estruturado e com metadados.
> **Arquivo no código:** [`ingestao/coletar.py`](../ingestao/coletar.py)
> **Comando:** `python -m ingestao.coletar`

## Fluxo

```
fontes.py ──► baixar página ──► é módulo de treinamento? ──sim──► descobrir unidades ──► baixar cada unidade
                                        │ não                                                   │
                                        ▼                                                       ▼
                                  limpar HTML  ◄────────────────────────────────────────────────┘
                                        │
                                        ▼
                          data/brutos/<pagina>.json
```

## Etapas

1. **Baixar** a página com `requests` (timeout de 30 s e pausa de 1 s entre páginas, para não sobrecarregar o site).
2. **Expandir módulos:** a página de um módulo de treinamento só lista as unidades. O código encontra os links das unidades (`1-...`, `2-...`) e baixa cada uma. Unidades de *knowledge check* (quiz) são ignoradas, pois não trazem explicação.
3. **Limpar o HTML** com `BeautifulSoup`:
   - Mantém só a área principal (`<main>`).
   - Remove `script`, `style`, `nav`, `aside`, `header`, `footer`, `form`, `button`.
   - Converte títulos em Markdown (`#`, `##`, `###`) para preservar a estrutura, que será usada na fragmentação.
4. **Salvar** um JSON por página.

## Formato de saída

```json
{
  "url": "https://learn.microsoft.com/pt-br/...",
  "area": "Arquitetura e serviços do Azure",
  "tipo": "treinamento",
  "titulo": "Descrever a redundância do armazenamento",
  "coletado_em": "2026-10-30",
  "texto": "# Título\n## Seção\nConteúdo..."
}
```

## Decisões e motivos

| Decisão | Motivo |
|---|---|
| Conteúdo em **pt-br** | Alunos brasileiros; o modelo de embeddings é multilíngue |
| Guardar **data da coleta** | Rastrear se o conteúdo está desatualizado (ver doc 07) |
| Manter **títulos** | Permite fragmentar por seção, sem misturar assuntos |
| Decodificar sempre em **UTF-8** | Sem isso, a biblioteca `requests` pode adivinhar a codificação errada e os acentos viram `redundÃ¢ncia` (bug encontrado e corrigido na Fase 1) |
| Falhas não interrompem o processo | Uma página fora do ar não derruba a coleta toda; as falhas são listadas no final |
