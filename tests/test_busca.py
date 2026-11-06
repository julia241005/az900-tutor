"""Busca por palavra exata (BM25), siglas e fusão de rankings (RRF)."""
from buscar import BM25, fusao_rrf, siglas, tokenizar


def test_tokenizar_remove_acentos_maiusculas_e_palavras_vazias():
    assert tokenizar("Qual é a Região do Armazenamento?") == ["regiao", "armazenamento"]


def test_siglas_reconhece_so_maiusculas():
    assert siglas("Diferença entre LRS e GRS no Azure") == {"lrs", "grs"}
    assert siglas("diferença entre lrs e grs") == set()


def test_bm25_coloca_primeiro_o_documento_com_a_palavra():
    docs = [tokenizar(t) for t in [
        "Zonas de disponibilidade protegem contra falhas de datacenter",
        "O armazenamento GRS copia os dados para uma região secundária",
        "Grupos de recursos organizam recursos do Azure",
    ]]
    notas = BM25(docs).pontuar(tokenizar("o que é GRS"))
    assert notas.argmax() == 1
    assert notas[0] == 0 and notas[2] == 0


def test_bm25_peso_extra_para_sigla():
    docs = [tokenizar("GRS replica dados"), tokenizar("replica replica dados dados")]
    bm = BM25(docs)
    consulta = tokenizar("GRS replica dados")
    sem_peso = bm.pontuar(consulta)
    com_peso = bm.pontuar(consulta, {"grs": 3.0})
    assert com_peso[0] > sem_peso[0]
    assert com_peso[1] == sem_peso[1]


def test_rrf_premia_quem_aparece_bem_nas_duas_listas():
    notas = fusao_rrf([[1, 2, 3], [3, 1, 4]])
    assert max(notas, key=notas.get) == 1     # 1º e 2º lugar → melhor soma
    assert notas[3] > notas[2]                # 3 aparece nas duas listas, 2 só em uma
    assert set(notas) == {1, 2, 3, 4}
