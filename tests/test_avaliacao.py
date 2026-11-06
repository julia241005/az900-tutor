"""O conjunto de avaliação está bem formado e a métrica de posição funciona."""
import avaliar


def test_conjunto_bem_formado():
    perguntas = avaliar.carregar_conjunto()
    ids = [q["id"] for q in perguntas]
    assert len(ids) == len(set(ids)), "ids repetidos"
    normais = [q for q in perguntas if not q.get("fora_do_escopo")]
    assert len(normais) >= 30
    for q in normais:
        assert q["fontes"] and q["palavras"], q["id"]


def test_posicao_da_fonte():
    trechos = [{"url": "https://x/azure/advisor"}, {"url": "https://x/storage/common/storage-redundancy"}]
    assert avaliar.posicao_da_fonte(trechos, ["storage-redundancy", "3-redundancy"]) == 2
    assert avaliar.posicao_da_fonte(trechos, ["purview"]) is None
