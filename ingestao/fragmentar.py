"""
ETAPA 2 da alimentação — FRAGMENTAR (chunking)
Um LLM não precisa (nem deve) ler a página inteira.
Quebramos cada página em pedaços pequenos, respeitando os títulos,
com uma pequena sobreposição para não cortar ideias no meio.

Rode:  python -m ingestao.fragmentar
"""
import json
import re

from config import ARQ_FRAGMENTOS, PASTA_BRUTOS, SOBREPOSICAO, TAMANHO_FRAGMENTO


def dividir_por_secoes(texto: str) -> list[tuple[str, str]]:
    """Separa o texto pelos títulos (## e ###). Retorna (titulo_secao, conteudo)."""
    partes = re.split(r"\n(?=#{1,3} )", texto)
    secoes = []
    for parte in partes:
        linhas = parte.strip().split("\n", 1)
        titulo = linhas[0].lstrip("# ").strip() if linhas[0].startswith("#") else ""
        conteudo = parte.strip()
        if conteudo:
            secoes.append((titulo, conteudo))
    return secoes


def dividir_por_tamanho(texto: str) -> list[str]:
    """Se a seção for grande, corta em janelas com sobreposição."""
    if len(texto) <= TAMANHO_FRAGMENTO:
        return [texto]
    pedacos, inicio = [], 0
    while inicio < len(texto):
        fim = inicio + TAMANHO_FRAGMENTO
        # tenta cortar no fim de uma frase/linha para não quebrar palavras
        corte = max(texto.rfind("\n", inicio, fim), texto.rfind(". ", inicio, fim))
        if corte > inicio + TAMANHO_FRAGMENTO // 2 and fim < len(texto):
            fim = corte + 1
        pedacos.append(texto[inicio:fim].strip())
        if fim >= len(texto):
            break
        inicio = fim - SOBREPOSICAO
        espaco = texto.find(" ", inicio, fim)  # começa numa palavra inteira
        if espaco != -1:
            inicio = espaco + 1
    return pedacos


def fragmentar_documento(doc: dict) -> list[dict]:
    fragmentos = []
    for titulo_secao, conteudo in dividir_por_secoes(doc["texto"]):
        for i, pedaco in enumerate(dividir_por_tamanho(conteudo)):
            if len(pedaco) < 80:  # ignora pedaços muito curtos (pouca informação)
                continue
            fragmentos.append({
                "id": f"{doc['url']}#{len(fragmentos)}",
                "texto": pedaco,
                # METADADOS: permitem filtrar e citar a fonte depois
                "url": doc["url"],
                "titulo": doc["titulo"],
                "secao": titulo_secao,
                "area": doc["area"],
                "tipo": doc.get("tipo", "documentacao"),
                "coletado_em": doc.get("coletado_em", ""),
            })
    return fragmentos


def main():
    todos = []
    for arquivo in sorted(PASTA_BRUTOS.glob("*.json")):
        doc = json.loads(arquivo.read_text(encoding="utf-8"))
        todos.extend(fragmentar_documento(doc))

    ARQ_FRAGMENTOS.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_FRAGMENTOS.open("w", encoding="utf-8") as f:
        for frag in todos:
            f.write(json.dumps(frag, ensure_ascii=False) + "\n")

    print(f"✅ {len(todos)} fragmentos criados em {ARQ_FRAGMENTOS.name}")
    if todos:
        media = sum(len(f["texto"]) for f in todos) // len(todos)
        print(f"   Tamanho médio: {media} caracteres (~{media // 4} tokens)")


if __name__ == "__main__":
    main()
