"""
ETAPA 1 da alimentação — COLETAR
Baixa cada página oficial, remove o "lixo" (menus, scripts, rodapé)
e salva só o texto útil, mantendo os títulos e os metadados.
Módulos de treinamento são expandidos automaticamente nas suas unidades.

Detalhes do processo: docs/02-ingestao-e-limpeza.md
Rode:  python -m ingestao.coletar
"""
import json
import re
import time
from datetime import date
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import PASTA_BRUTOS
from ingestao.fontes import FONTES

CABECALHO = {"User-Agent": "AZ900-Tutor/1.0 (projeto de estudo)"}
PAUSA_SEGUNDOS = 1  # educação: não sobrecarregar o site
IGNORAR_UNIDADES = ("knowledge-check",)  # unidades de quiz não trazem conteúdo explicativo
# Frases do site que não são conteúdo (avisos de login, rodapés etc.)
RUIDOS = (
    "O acesso a essa página exige autorização",
    "Este navegador não tem mais suporte",
    "Atualize para o Microsoft Edge",
)


def baixar(url: str) -> str:
    resp = requests.get(url, headers=CABECALHO, timeout=30)
    resp.raise_for_status()
    time.sleep(PAUSA_SEGUNDOS)
    # Força UTF-8: sem isso, acentos viram "redundÃ¢ncia" (erro de codificação)
    return resp.content.decode("utf-8", errors="replace")


def limpar_html(html: str) -> tuple[str, str]:
    """Extrai título e texto principal da página, em formato Markdown simples."""
    soup = BeautifulSoup(html, "html.parser")
    titulo = soup.title.get_text(strip=True) if soup.title else "Sem título"
    titulo = titulo.split("|")[0].strip()

    principal = soup.find("main") or soup.body or soup
    for tag in principal.find_all(["script", "style", "nav", "aside", "header", "footer", "form", "button"]):
        tag.decompose()

    linhas = []
    for el in principal.find_all(["h1", "h2", "h3", "p", "li", "td"]):
        texto = el.get_text(" ", strip=True)
        if not texto or any(r in texto for r in RUIDOS):
            continue
        if el.name == "h1":
            linhas.append(f"\n# {texto}")
        elif el.name == "h2":
            linhas.append(f"\n## {texto}")
        elif el.name == "h3":
            linhas.append(f"\n### {texto}")
        elif el.name == "li":
            linhas.append(f"- {texto}")
        else:
            linhas.append(texto)

    texto = "\n".join(linhas)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return titulo, texto


def unidades_do_modulo(url_modulo: str, html: str) -> list[str]:
    """Encontra os links das unidades de um módulo (ex.: .../describe-cloud-compute/2-introduction...)."""
    caminho_modulo = urlparse(url_modulo).path.rstrip("/") + "/"
    soup = BeautifulSoup(html, "html.parser")
    unidades = []
    for a in soup.find_all("a", href=True):
        url = urljoin(url_modulo, a["href"]).split("#")[0].split("?")[0]
        caminho = urlparse(url).path
        if not caminho.startswith(caminho_modulo):
            continue
        resto = caminho[len(caminho_modulo):].strip("/")
        if re.match(r"^\d+-", resto) and not any(p in resto for p in IGNORAR_UNIDADES):
            if url not in unidades:
                unidades.append(url)
    return sorted(unidades, key=lambda u: int(re.search(r"/(\d+)-[^/]*$", u).group(1)))


def nome_arquivo(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", url.split("/pt-br/")[-1].lower()).strip("_") + ".json"


def salvar(url: str, fonte: dict, html: str) -> int:
    titulo, texto = limpar_html(html)
    doc = {
        "url": url,
        "area": fonte["area"],
        "tipo": fonte["tipo"],
        "titulo": titulo,
        "coletado_em": date.today().isoformat(),
        "texto": texto,
    }
    (PASTA_BRUTOS / nome_arquivo(url)).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {titulo[:65]}  ({len(texto):,} caracteres)")
    return 1


def main():
    PASTA_BRUTOS.mkdir(parents=True, exist_ok=True)
    ok, falhas = 0, []

    for fonte in FONTES:
        url = fonte["url"]
        try:
            html = baixar(url)
            if fonte["tipo"] == "treinamento":
                unidades = unidades_do_modulo(url, html)
                print(f"📘 Módulo: {url.rstrip('/').split('/')[-1]}  ({len(unidades)} unidades)")
                for u in unidades:
                    try:
                        ok += salvar(u, fonte, baixar(u))
                    except Exception as erro:
                        falhas.append(u)
                        print(f"  ❌ {u}  →  {erro}")
            else:
                ok += salvar(url, fonte, html)
        except Exception as erro:
            falhas.append(url)
            print(f"❌ {url}  →  {erro}")

    print(f"\nColetadas: {ok} páginas | Falhas: {len(falhas)}")
    if falhas:
        print("Falharam (verifique os links em fontes.py):")
        for f in falhas:
            print("  -", f)


if __name__ == "__main__":
    main()
