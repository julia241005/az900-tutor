"""
trilhas.py — CATÁLOGO DE CERTIFICAÇÕES (o coração multi-certificação do tutor).

Antes, o tutor era fixo no AZ-900. Agora cada certificação é uma "trilha"
selecionável: um perfil com nome, provedor, área de foco, as áreas do exame
(com seus pesos), as fontes oficiais da documentação e o banco de perguntas.

O usuário escolhe a trilha e TUDO passa a responder, simular e medir progresso
para aquela certificação: o prompt do tutor, a busca (coleção de vetores),
o simulado e o painel de progresso.

Como adicionar uma nova certificação:
  1. Crie uma Trilha aqui no CATALOGO (áreas, pesos, palavras e fontes oficiais).
  2. Crie perguntas/<id>.json com algumas perguntas curadas (ver perguntas/curadas.json).
  3. Rode a ingestão daquela trilha:
        python -m ingestao.coletar    --trilha <id>
        python -m ingestao.fragmentar --trilha <id>
        python -m ingestao.indexar    --trilha <id>
        python importar_perguntas.py  --trilha <id>

Este módulo não importa nada do projeto (fica na base das dependências), para
evitar imports circulares: config, fontes e o resto é que importam daqui.
"""
from dataclasses import dataclass, field

# ── Áreas de foco (agrupam as trilhas na interface) ──────────────────────────
FOCO_INFRA = "Infraestrutura / Nuvem"
FOCO_REDES = "Redes"
FOCO_DEVOPS = "DevOps"
FOCO_SEGURANCA = "Segurança"

ORDEM_FOCO = [FOCO_INFRA, FOCO_REDES, FOCO_DEVOPS, FOCO_SEGURANCA]


@dataclass(frozen=True)
class Area:
    """Uma área (domínio) do exame, com peso e palavras que ajudam o roteador do simulado."""
    nome: str
    peso: float            # peso numérico aproximado (%), usado para ordenar e priorizar
    peso_label: str        # rótulo exibido (ex.: "25–30%")
    palavras: tuple = ()   # termos que, na mensagem do aluno, indicam esta área


@dataclass(frozen=True)
class Trilha:
    id: str                # identificador curto (slug): az900, aws-clf-c02...
    sigla: str             # AZ-900, CLF-C02...
    titulo: str            # nome completo da certificação
    provedor: str          # Microsoft Azure, AWS, Cisco, CompTIA, HashiCorp, CNCF
    foco: str              # uma das áreas de foco acima
    inicial: str           # letra do "selo" na interface
    cor: str               # cor de destaque (hex) na interface
    colecao: str           # nome da coleção de vetores (ChromaDB)
    descricao: str
    areas: tuple           # tuple[Area, ...] — áreas do exame com pesos
    fontes: tuple          # tuple[dict, ...] — {"tipo", "area", "url"}
    perguntas_arquivo: str # caminho do banco de perguntas (relativo à raiz)
    base_doc: str = ""     # URL base da documentação (informativo)
    pronta: bool = False   # True quando já tem fontes + perguntas curadas revisadas

    @property
    def nomes_areas(self):
        return [a.nome for a in self.areas]

    def area_maior_peso(self):
        return max(self.areas, key=lambda a: a.peso)


def _fonte(tipo, area, url):
    return {"tipo": tipo, "area": area, "url": url}


# ═════════════════════════════════════════════════════════════════════════════
#  INFRAESTRUTURA / NUVEM
# ═════════════════════════════════════════════════════════════════════════════

# ── AZ-900 (trilha de referência, 100% pronta) ───────────────────────────────
_MS = "https://learn.microsoft.com/pt-br"
_MOD = f"{_MS}/training/modules"

_AZ900_CONCEITOS = "Conceitos de nuvem"
_AZ900_ARQ = "Arquitetura e serviços do Azure"
_AZ900_GOV = "Gestão e governança do Azure"
_AZ900_GERAL = "Geral"

AZ900 = Trilha(
    id="az900", sigla="AZ-900", titulo="Microsoft Azure Fundamentals",
    provedor="Microsoft Azure", foco=FOCO_INFRA, inicial="A", cor="#0078d4",
    colecao="az900", base_doc=_MS, pronta=True,
    perguntas_arquivo="perguntas/curadas.json",
    descricao="Fundamentos de nuvem e dos serviços do Microsoft Azure.",
    areas=(
        Area(_AZ900_CONCEITOS, 27, "25–30%",
             ("conceitos", "conceito", "nuvem", "iaas", "paas", "saas")),
        Area(_AZ900_ARQ, 37, "35–40%",
             ("arquitetura", "servicos", "rede", "armazenamento", "computacao", "identidade", "seguranca")),
        Area(_AZ900_GOV, 32, "30–35%",
             ("governanca", "gestao", "custo", "custos", "policy", "bloqueio", "monitor", "conformidade")),
    ),
    fontes=(
        _fonte("guia", _AZ900_GERAL, f"{_MS}/credentials/certifications/resources/study-guides/az-900"),
        _fonte("treinamento", _AZ900_CONCEITOS, f"{_MOD}/describe-cloud-compute/"),
        _fonte("treinamento", _AZ900_CONCEITOS, f"{_MOD}/describe-benefits-use-cloud-services/"),
        _fonte("treinamento", _AZ900_CONCEITOS, f"{_MOD}/describe-cloud-service-types/"),
        _fonte("treinamento", _AZ900_ARQ, f"{_MOD}/describe-core-architectural-components-of-azure/"),
        _fonte("treinamento", _AZ900_ARQ, f"{_MOD}/describe-azure-compute-networking-services/"),
        _fonte("treinamento", _AZ900_ARQ, f"{_MOD}/describe-azure-networking-services/"),
        _fonte("treinamento", _AZ900_ARQ, f"{_MOD}/describe-azure-storage-services/"),
        _fonte("treinamento", _AZ900_ARQ, f"{_MOD}/describe-azure-identity-access-security/"),
        _fonte("treinamento", _AZ900_GOV, f"{_MOD}/describe-cost-management-azure/"),
        _fonte("treinamento", _AZ900_GOV, f"{_MOD}/describe-features-tools-azure-for-governance-compliance/"),
        _fonte("treinamento", _AZ900_GOV, f"{_MOD}/describe-features-tools-manage-deploy-azure-resources/"),
        _fonte("treinamento", _AZ900_GOV, f"{_MOD}/describe-monitoring-tools-azure/"),
        _fonte("documentacao", _AZ900_CONCEITOS, f"{_MS}/azure/security/fundamentals/shared-responsibility"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/reliability/availability-zones-overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/azure-resource-manager/management/overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/governance/management-groups/overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/virtual-machines/overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/app-service/overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/azure-functions/functions-overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/container-instances/container-instances-overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/aks/what-is-aks"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/virtual-network/virtual-networks-overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/vpn-gateway/vpn-gateway-about-vpngateways"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/expressroute/expressroute-introduction"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/storage/common/storage-introduction"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/storage/common/storage-redundancy"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/storage/blobs/access-tiers-overview"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/entra/fundamentals/whatis"),
        _fonte("documentacao", _AZ900_ARQ, f"{_MS}/azure/role-based-access-control/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/cost-management-billing/costs/overview-cost-management"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/azure-resource-manager/management/tag-resources"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/governance/policy/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/azure-resource-manager/management/lock-resources"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/azure-arc/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/azure-resource-manager/templates/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/advisor/advisor-overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/azure-monitor/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/service-health/overview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/purview/purview"),
        _fonte("documentacao", _AZ900_GOV, f"{_MS}/azure/defender-for-cloud/defender-for-cloud-introduction"),
    ),
)

# ── AWS CLF-C02 (Cloud Practitioner) ─────────────────────────────────────────
_AWS = "https://docs.aws.amazon.com"
_CLF_CONCEITOS = "Conceitos de Nuvem"
_CLF_SEG = "Segurança e Conformidade"
_CLF_TEC = "Tecnologia e Serviços de Nuvem"
_CLF_BILL = "Cobrança, Preços e Suporte"

AWS_CLF = Trilha(
    id="aws-clf-c02", sigla="CLF-C02", titulo="AWS Certified Cloud Practitioner",
    provedor="Amazon Web Services", foco=FOCO_INFRA, inicial="W", cor="#ff9900",
    colecao="aws_clf_c02", base_doc=_AWS,
    perguntas_arquivo="perguntas/aws-clf-c02.json",
    descricao="Fundamentos da nuvem AWS: conceitos, segurança, serviços e custos.",
    areas=(
        Area(_CLF_CONCEITOS, 24, "24%",
             ("conceitos", "nuvem", "cloud", "well-architected", "iaas", "paas", "saas", "beneficios")),
        Area(_CLF_SEG, 30, "30%",
             ("seguranca", "iam", "mfa", "shield", "waf", "kms", "conformidade", "responsabilidade")),
        Area(_CLF_TEC, 34, "34%",
             ("ec2", "s3", "rds", "lambda", "vpc", "rede", "armazenamento", "computacao", "servico", "servicos")),
        Area(_CLF_BILL, 12, "12%",
             ("custo", "custos", "preco", "precos", "cobranca", "suporte", "billing", "budget")),
    ),
    fontes=(
        _fonte("documentacao", _CLF_CONCEITOS, "https://aws.amazon.com/what-is-cloud-computing/"),
        _fonte("documentacao", _CLF_CONCEITOS, "https://aws.amazon.com/types-of-cloud-computing/"),
        _fonte("documentacao", _CLF_CONCEITOS, f"{_AWS}/wellarchitected/latest/framework/welcome.html"),
        _fonte("documentacao", _CLF_CONCEITOS, f"{_AWS}/whitepapers/latest/aws-overview/introduction.html"),
        _fonte("documentacao", _CLF_SEG, "https://aws.amazon.com/compliance/shared-responsibility-model/"),
        _fonte("documentacao", _CLF_SEG, f"{_AWS}/IAM/latest/UserGuide/introduction.html"),
        _fonte("documentacao", _CLF_SEG, f"{_AWS}/whitepapers/latest/introduction-aws-security/introduction-aws-security.html"),
        _fonte("documentacao", _CLF_SEG, "https://aws.amazon.com/shield/"),
        _fonte("documentacao", _CLF_SEG, "https://aws.amazon.com/waf/"),
        _fonte("documentacao", _CLF_TEC, f"{_AWS}/AWSEC2/latest/UserGuide/concepts.html"),
        _fonte("documentacao", _CLF_TEC, f"{_AWS}/AmazonS3/latest/userguide/Welcome.html"),
        _fonte("documentacao", _CLF_TEC, f"{_AWS}/AmazonRDS/latest/UserGuide/Welcome.html"),
        _fonte("documentacao", _CLF_TEC, f"{_AWS}/lambda/latest/dg/welcome.html"),
        _fonte("documentacao", _CLF_TEC, f"{_AWS}/vpc/latest/userguide/what-is-amazon-vpc.html"),
        _fonte("documentacao", _CLF_TEC, "https://aws.amazon.com/about-aws/global-infrastructure/"),
        _fonte("documentacao", _CLF_BILL, "https://aws.amazon.com/pricing/"),
        _fonte("documentacao", _CLF_BILL, f"{_AWS}/awsaccountbilling/latest/aboutv2/billing-what-is.html"),
        _fonte("documentacao", _CLF_BILL, "https://aws.amazon.com/premiumsupport/plans/"),
    ),
)

# ── AZ-104 (Azure Administrator) ─────────────────────────────────────────────
_104_ID = "Identidade e governança"
_104_STORAGE = "Armazenamento"
_104_COMPUTE = "Computação"
_104_NET = "Rede virtual"
_104_MON = "Monitoramento e manutenção"

AZ104 = Trilha(
    id="az104", sigla="AZ-104", titulo="Microsoft Azure Administrator",
    provedor="Microsoft Azure", foco=FOCO_INFRA, inicial="A", cor="#0063b1",
    colecao="az104", base_doc=_MS,
    perguntas_arquivo="perguntas/az104.json",
    descricao="Administração do Azure: identidades, armazenamento, computação, rede e monitoramento.",
    areas=(
        Area(_104_ID, 22, "20–25%", ("identidade", "governanca", "entra", "rbac", "assinatura", "politica")),
        Area(_104_STORAGE, 17, "15–20%", ("armazenamento", "storage", "blob", "arquivo", "backup")),
        Area(_104_COMPUTE, 22, "20–25%", ("computacao", "vm", "maquina", "container", "app", "escala")),
        Area(_104_NET, 17, "15–20%", ("rede", "vnet", "dns", "balanceador", "gateway", "firewall")),
        Area(_104_MON, 12, "10–15%", ("monitor", "manutencao", "backup", "recuperacao", "alerta")),
    ),
    fontes=(
        _fonte("documentacao", _104_ID, f"{_MS}/entra/fundamentals/whatis"),
        _fonte("documentacao", _104_ID, f"{_MS}/azure/role-based-access-control/overview"),
        _fonte("documentacao", _104_STORAGE, f"{_MS}/azure/storage/common/storage-introduction"),
        _fonte("documentacao", _104_STORAGE, f"{_MS}/azure/storage/blobs/storage-blobs-introduction"),
        _fonte("documentacao", _104_COMPUTE, f"{_MS}/azure/virtual-machines/overview"),
        _fonte("documentacao", _104_COMPUTE, f"{_MS}/azure/virtual-machine-scale-sets/overview"),
        _fonte("documentacao", _104_NET, f"{_MS}/azure/virtual-network/virtual-networks-overview"),
        _fonte("documentacao", _104_NET, f"{_MS}/azure/load-balancer/load-balancer-overview"),
        _fonte("documentacao", _104_MON, f"{_MS}/azure/azure-monitor/overview"),
        _fonte("documentacao", _104_MON, f"{_MS}/azure/backup/backup-overview"),
    ),
)

# ═════════════════════════════════════════════════════════════════════════════
#  REDES
# ═════════════════════════════════════════════════════════════════════════════
_REDES_FUND = "Fundamentos de rede"
_REDES_INFRA = "Infraestrutura e conectividade"
_REDES_OPS = "Operações e segurança de rede"

CCNA = Trilha(
    id="ccna", sigla="CCNA", titulo="Cisco Certified Network Associate (200-301)",
    provedor="Cisco", foco=FOCO_REDES, inicial="C", cor="#1ba0d7",
    colecao="ccna", base_doc="https://www.cisco.com",
    perguntas_arquivo="perguntas/ccna.json",
    descricao="Fundamentos de redes Cisco: IP, roteamento, switching, segurança e automação.",
    areas=(
        Area(_REDES_FUND, 20, "~20%", ("fundamentos", "osi", "tcp", "ip", "sub-rede", "subnet", "ethernet")),
        Area("Acesso à rede", 20, "~20%", ("switch", "vlan", "trunk", "wireless", "stp")),
        Area("Conectividade IP", 25, "~25%", ("roteamento", "ospf", "rota", "gateway", "ipv6")),
        Area("Serviços IP", 10, "~10%", ("nat", "dhcp", "dns", "ntp", "qos")),
        Area(_REDES_OPS, 15, "~15%", ("seguranca", "acl", "firewall", "vpn", "porta")),
        Area("Automação", 10, "~10%", ("automacao", "rest", "api", "sdn", "python")),
    ),
    fontes=(
        _fonte("documentacao", _REDES_FUND, "https://www.cloudflare.com/learning/network-layer/what-is-the-osi-model/"),
        _fonte("documentacao", _REDES_FUND, "https://www.cloudflare.com/learning/ddos/glossary/tcp-ip/"),
        _fonte("documentacao", "Conectividade IP", "https://www.cloudflare.com/learning/network-layer/what-is-routing/"),
    ),
)

NETWORK_PLUS = Trilha(
    id="network-plus", sigla="N10-009", titulo="CompTIA Network+",
    provedor="CompTIA", foco=FOCO_REDES, inicial="N", cor="#c8202f",
    colecao="network_plus", base_doc="https://www.comptia.org",
    perguntas_arquivo="perguntas/network-plus.json",
    descricao="Redes de forma neutra (sem fabricante): conceitos, implementação, operação e segurança.",
    areas=(
        Area("Conceitos de rede", 23, "23%", ("conceitos", "osi", "tcp", "ip", "porta", "protocolo")),
        Area("Implementação", 20, "20%", ("implementacao", "cabo", "switch", "roteador", "topologia")),
        Area("Operações de rede", 19, "19%", ("operacoes", "monitor", "documentacao", "disponibilidade")),
        Area("Segurança de rede", 19, "19%", ("seguranca", "firewall", "vpn", "acl", "ataque")),
        Area("Solução de problemas", 19, "19%", ("problema", "troubleshooting", "latencia", "perda")),
    ),
    fontes=(
        _fonte("documentacao", "Conceitos de rede", "https://www.cloudflare.com/learning/network-layer/what-is-the-osi-model/"),
        _fonte("documentacao", "Segurança de rede", "https://www.cloudflare.com/learning/access-management/what-is-a-vpn/"),
    ),
)

# ═════════════════════════════════════════════════════════════════════════════
#  DEVOPS
# ═════════════════════════════════════════════════════════════════════════════
_HC = "https://developer.hashicorp.com/terraform"

TERRAFORM = Trilha(
    id="terraform-associate", sigla="TF-003", titulo="HashiCorp Terraform Associate",
    provedor="HashiCorp", foco=FOCO_DEVOPS, inicial="T", cor="#7b42bc",
    colecao="terraform_associate", base_doc=_HC,
    perguntas_arquivo="perguntas/terraform-associate.json",
    descricao="Infraestrutura como código com Terraform: fluxo, estado, módulos e provisionamento.",
    areas=(
        Area("Conceitos de IaC", 15, "~15%", ("iac", "infraestrutura", "codigo", "conceito")),
        Area("Fluxo do Terraform", 25, "~25%", ("init", "plan", "apply", "destroy", "fluxo", "workflow")),
        Area("Estado (state)", 20, "~20%", ("state", "estado", "backend", "remoto", "lock")),
        Area("Módulos e provedores", 20, "~20%", ("modulo", "modulos", "provider", "provedor", "registry")),
        Area("HCP e boas práticas", 20, "~20%", ("hcp", "cloud", "workspace", "variavel", "output")),
    ),
    fontes=(
        _fonte("documentacao", "Conceitos de IaC", f"{_HC}/intro"),
        _fonte("documentacao", "Fluxo do Terraform", f"{_HC}/cli/commands"),
        _fonte("documentacao", "Estado (state)", f"{_HC}/language/state"),
        _fonte("documentacao", "Módulos e provedores", f"{_HC}/language/modules"),
    ),
)

KCNA = Trilha(
    id="kcna", sigla="KCNA", titulo="Kubernetes and Cloud Native Associate",
    provedor="CNCF", foco=FOCO_DEVOPS, inicial="K", cor="#326ce5",
    colecao="kcna", base_doc="https://kubernetes.io/docs",
    perguntas_arquivo="perguntas/kcna.json",
    descricao="Fundamentos de Kubernetes e do ecossistema cloud native (contêineres, CI/CD, observabilidade).",
    areas=(
        Area("Fundamentos do Kubernetes", 46, "46%", ("kubernetes", "pod", "node", "cluster", "kubectl", "api")),
        Area("Orquestração de contêineres", 22, "22%", ("container", "docker", "imagem", "runtime", "rede")),
        Area("Arquitetura cloud native", 16, "16%", ("cloud native", "microsservico", "autoscaling", "serverless")),
        Area("Entrega cloud native", 8, "8%", ("ci", "cd", "gitops", "entrega", "pipeline")),
        Area("Observabilidade", 8, "8%", ("observabilidade", "metrica", "log", "prometheus", "telemetria")),
    ),
    fontes=(
        _fonte("documentacao", "Fundamentos do Kubernetes", "https://kubernetes.io/docs/concepts/overview/"),
        _fonte("documentacao", "Fundamentos do Kubernetes", "https://kubernetes.io/docs/concepts/workloads/pods/"),
        _fonte("documentacao", "Orquestração de contêineres", "https://kubernetes.io/docs/concepts/containers/"),
    ),
)

# ═════════════════════════════════════════════════════════════════════════════
#  SEGURANÇA
# ═════════════════════════════════════════════════════════════════════════════
SECURITY_PLUS = Trilha(
    id="security-plus", sigla="SY0-701", titulo="CompTIA Security+",
    provedor="CompTIA", foco=FOCO_SEGURANCA, inicial="S", cor="#c8202f",
    colecao="security_plus", base_doc="https://www.comptia.org",
    perguntas_arquivo="perguntas/security-plus.json",
    descricao="Segurança da informação de forma neutra: ameaças, arquitetura, operações e governança.",
    areas=(
        Area("Conceitos gerais de segurança", 12, "12%", ("conceitos", "cia", "controle", "criptografia", "zero trust")),
        Area("Ameaças e vulnerabilidades", 22, "22%", ("ameaca", "vulnerabilidade", "malware", "phishing", "ataque")),
        Area("Arquitetura de segurança", 18, "18%", ("arquitetura", "rede", "nuvem", "firewall", "segmentacao")),
        Area("Operações de segurança", 28, "28%", ("operacoes", "iam", "monitor", "resposta", "incidente", "hardening")),
        Area("Governança e risco", 20, "20%", ("governanca", "risco", "conformidade", "politica", "auditoria")),
    ),
    fontes=(
        _fonte("documentacao", "Conceitos gerais de segurança", "https://www.cloudflare.com/learning/security/glossary/what-is-encryption/"),
        _fonte("documentacao", "Ameaças e vulnerabilidades", "https://www.cloudflare.com/learning/security/threats/phishing-attack/"),
        _fonte("documentacao", "Arquitetura de segurança", "https://www.cloudflare.com/learning/security/glossary/what-is-zero-trust/"),
    ),
)

SC900 = Trilha(
    id="sc900", sigla="SC-900", titulo="Microsoft Security, Compliance, and Identity Fundamentals",
    provedor="Microsoft", foco=FOCO_SEGURANCA, inicial="S", cor="#0078d4",
    colecao="sc900", base_doc=_MS,
    perguntas_arquivo="perguntas/sc900.json",
    descricao="Fundamentos de segurança, conformidade e identidade da Microsoft.",
    areas=(
        Area("Conceitos de segurança e conformidade", 12, "10–15%", ("conceitos", "zero trust", "criptografia", "responsabilidade")),
        Area("Identidade (Microsoft Entra)", 30, "25–30%", ("identidade", "entra", "autenticacao", "mfa", "condicional")),
        Area("Soluções de segurança", 30, "25–30%", ("defender", "sentinel", "seguranca", "firewall")),
        Area("Conformidade (Microsoft Purview)", 28, "25–30%", ("conformidade", "purview", "rotulo", "dlp", "risco")),
    ),
    fontes=(
        _fonte("documentacao", "Identidade (Microsoft Entra)", f"{_MS}/entra/fundamentals/whatis"),
        _fonte("documentacao", "Soluções de segurança", f"{_MS}/azure/defender-for-cloud/defender-for-cloud-introduction"),
        _fonte("documentacao", "Conformidade (Microsoft Purview)", f"{_MS}/purview/purview"),
    ),
)

AZ500 = Trilha(
    id="az500", sigla="AZ-500", titulo="Microsoft Azure Security Engineer",
    provedor="Microsoft Azure", foco=FOCO_SEGURANCA, inicial="A", cor="#0063b1",
    colecao="az500", base_doc=_MS,
    perguntas_arquivo="perguntas/az500.json",
    descricao="Engenharia de segurança no Azure: identidade, plataforma, dados/apps e operações.",
    areas=(
        Area("Identidade e acesso", 28, "25–30%", ("identidade", "acesso", "entra", "rbac", "pim", "condicional")),
        Area("Proteção de plataforma", 25, "20–25%", ("plataforma", "rede", "firewall", "nsg", "bastion")),
        Area("Dados e aplicações", 25, "20–25%", ("dados", "aplicacao", "key vault", "criptografia", "sql")),
        Area("Operações de segurança", 27, "25–30%", ("operacoes", "defender", "sentinel", "monitor", "incidente")),
    ),
    fontes=(
        _fonte("documentacao", "Identidade e acesso", f"{_MS}/entra/identity/role-based-access-control/custom-overview"),
        _fonte("documentacao", "Proteção de plataforma", f"{_MS}/azure/firewall/overview"),
        _fonte("documentacao", "Dados e aplicações", f"{_MS}/azure/key-vault/general/overview"),
        _fonte("documentacao", "Operações de segurança", f"{_MS}/azure/sentinel/overview"),
    ),
)


# ── Registro central ─────────────────────────────────────────────────────────
_TODAS = [AZ900, AWS_CLF, AZ104, CCNA, NETWORK_PLUS, TERRAFORM, KCNA, SECURITY_PLUS, SC900, AZ500]
CATALOGO = {t.id: t for t in _TODAS}

TRILHA_PADRAO = "az900"


def obter(trilha_id: str | None) -> Trilha:
    """Devolve a trilha pelo id. Se não existir (ou None), cai na trilha padrão."""
    if not trilha_id:
        return CATALOGO[TRILHA_PADRAO]
    return CATALOGO.get(trilha_id, CATALOGO[TRILHA_PADRAO])


def existe(trilha_id: str) -> bool:
    return trilha_id in CATALOGO


def listar() -> list[Trilha]:
    return list(_TODAS)


def por_foco() -> list[tuple]:
    """Retorna [(area_de_foco, [trilhas...]), ...] na ordem de ORDEM_FOCO, para a interface."""
    grupos = []
    for foco in ORDEM_FOCO:
        trilhas = [t for t in _TODAS if t.foco == foco]
        if trilhas:
            grupos.append((foco, trilhas))
    return grupos


def resumo(trilha: Trilha) -> dict:
    """Dados leves da trilha para enviar à interface (sem as fontes, que são grandes)."""
    return {
        "id": trilha.id, "sigla": trilha.sigla, "titulo": trilha.titulo,
        "provedor": trilha.provedor, "foco": trilha.foco, "inicial": trilha.inicial,
        "cor": trilha.cor, "descricao": trilha.descricao, "pronta": trilha.pronta,
        "areas": [{"nome": a.nome, "peso": a.peso_label} for a in trilha.areas],
    }
