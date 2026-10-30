"""
fontes.py — Catálogo de fontes do tutor (de onde vem o conhecimento).
Detalhes de cada fonte e licença: docs/01-fontes-de-dados.md

Tipos de fonte:
  - "guia"         → Guia de estudo oficial (o que cai no exame)
  - "treinamento"  → Módulos da trilha oficial AZ-900 (cada módulo é expandido nas suas unidades)
  - "documentacao" → Documentação técnica do Azure
"""

AREA_CONCEITOS = "Conceitos de nuvem"
AREA_ARQUITETURA = "Arquitetura e serviços do Azure"
AREA_GOVERNANCA = "Gestão e governança do Azure"
AREA_GERAL = "Geral"

BASE = "https://learn.microsoft.com/pt-br"
MOD = f"{BASE}/training/modules"

FONTES = [
    # ── GUIA DE ESTUDO (esqueleto do exame) ───────────────────────────────
    {"tipo": "guia", "area": AREA_GERAL,
     "url": f"{BASE}/credentials/certifications/resources/study-guides/az-900"},

    # ── TRILHA OFICIAL DE TREINAMENTO AZ-900 ──────────────────────────────
    {"tipo": "treinamento", "area": AREA_CONCEITOS, "url": f"{MOD}/describe-cloud-compute/"},
    {"tipo": "treinamento", "area": AREA_CONCEITOS, "url": f"{MOD}/describe-benefits-use-cloud-services/"},
    {"tipo": "treinamento", "area": AREA_CONCEITOS, "url": f"{MOD}/describe-cloud-service-types/"},

    {"tipo": "treinamento", "area": AREA_ARQUITETURA, "url": f"{MOD}/describe-core-architectural-components-of-azure/"},
    {"tipo": "treinamento", "area": AREA_ARQUITETURA, "url": f"{MOD}/describe-azure-compute-networking-services/"},
    {"tipo": "treinamento", "area": AREA_ARQUITETURA, "url": f"{MOD}/describe-azure-networking-services/"},
    {"tipo": "treinamento", "area": AREA_ARQUITETURA, "url": f"{MOD}/describe-azure-storage-services/"},
    {"tipo": "treinamento", "area": AREA_ARQUITETURA, "url": f"{MOD}/describe-azure-identity-access-security/"},

    {"tipo": "treinamento", "area": AREA_GOVERNANCA, "url": f"{MOD}/describe-cost-management-azure/"},
    {"tipo": "treinamento", "area": AREA_GOVERNANCA, "url": f"{MOD}/describe-features-tools-azure-for-governance-compliance/"},
    {"tipo": "treinamento", "area": AREA_GOVERNANCA, "url": f"{MOD}/describe-features-tools-manage-deploy-azure-resources/"},
    {"tipo": "treinamento", "area": AREA_GOVERNANCA, "url": f"{MOD}/describe-monitoring-tools-azure/"},

    # ── DOCUMENTAÇÃO TÉCNICA (aprofundamento) ─────────────────────────────
    {"tipo": "documentacao", "area": AREA_CONCEITOS, "url": f"{BASE}/azure/security/fundamentals/shared-responsibility"},

    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/reliability/availability-zones-overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/azure-resource-manager/management/overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/governance/management-groups/overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/virtual-machines/overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/app-service/overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/azure-functions/functions-overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/container-instances/container-instances-overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/aks/what-is-aks"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/virtual-network/virtual-networks-overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/vpn-gateway/vpn-gateway-about-vpngateways"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/expressroute/expressroute-introduction"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/storage/common/storage-introduction"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/storage/common/storage-redundancy"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/storage/blobs/access-tiers-overview"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/entra/fundamentals/whatis"},
    {"tipo": "documentacao", "area": AREA_ARQUITETURA, "url": f"{BASE}/azure/role-based-access-control/overview"},

    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/cost-management-billing/costs/overview-cost-management"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/azure-resource-manager/management/tag-resources"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/governance/policy/overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/azure-resource-manager/management/lock-resources"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/azure-arc/overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/azure-resource-manager/templates/overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/advisor/advisor-overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/azure-monitor/overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/service-health/overview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/purview/purview"},
    {"tipo": "documentacao", "area": AREA_GOVERNANCA, "url": f"{BASE}/azure/defender-for-cloud/defender-for-cloud-introduction"},
]
