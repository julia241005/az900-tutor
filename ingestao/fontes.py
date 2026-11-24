"""
fontes.py — Compatibilidade e atalhos para as fontes das trilhas.

As fontes (de onde vem o conhecimento) agora moram no catálogo de trilhas
(trilhas.py), uma lista por certificação. Este módulo:
  - reexporta as áreas e as fontes do AZ-900 (trilha padrão), para manter
    compatibilidade com o código e os testes antigos;
  - oferece `fontes_da_trilha(id)` para a ingestão de qualquer trilha.

Tipos de fonte:
  - "guia"         → Guia de estudo oficial (o que cai no exame)
  - "treinamento"  → Módulos de trilha oficial (cada módulo é expandido nas unidades)
  - "documentacao" → Documentação técnica
"""
import trilhas

# ── Áreas do AZ-900 (mantidas para compatibilidade com testes e código antigo) ──
AREA_CONCEITOS = "Conceitos de nuvem"
AREA_ARQUITETURA = "Arquitetura e serviços do Azure"
AREA_GOVERNANCA = "Gestão e governança do Azure"
AREA_GERAL = "Geral"


def fontes_da_trilha(trilha_id: str | None = None) -> list[dict]:
    """Lista de fontes {tipo, area, url} de uma trilha (padrão: a trilha ativa)."""
    return [dict(f) for f in trilhas.obter(trilha_id).fontes]


# Fontes da trilha padrão (AZ-900), para quem importa `FONTES` diretamente.
FONTES = fontes_da_trilha(trilhas.TRILHA_PADRAO)
