"""Memória: histórico do chat salvo no banco e progresso do simulado."""
import banco
import sessao
import simulado


def test_historico_sobrevive_ao_reiniciar_o_tutor():
    s = sessao.obter_sessao("aluna")
    s.lembrar("user", "O que é GRS?")
    s.lembrar("assistant", "GRS copia para outra região [1].", {"fontes": [{"numero": 1}]})

    sessao._SESSOES.clear()                      # simula fechar e abrir o tutor
    s2 = sessao.obter_sessao("aluna")
    assert [m["content"] for m in s2.historico] == ["O que é GRS?", "GRS copia para outra região [1]."]
    assert banco.mensagens_da_sessao("aluna")[1]["extra"]["fontes"][0]["numero"] == 1


def test_llm_recebe_so_as_ultimas_mensagens():
    s = sessao.obter_sessao("aluna")
    for i in range(sessao.MAX_HISTORICO + 5):
        s.lembrar("user", f"mensagem {i}")
    sessao._SESSOES.clear()
    assert len(sessao.obter_sessao("aluna").historico) == sessao.MAX_HISTORICO
    assert len(banco.mensagens_da_sessao("aluna", 100)) == sessao.MAX_HISTORICO + 5


def test_nova_conversa_apaga_historico_mas_nao_o_progresso(pergunta_exemplo):
    s = sessao.obter_sessao("aluna")
    s.lembrar("user", "oi")
    banco.registrar_resposta("aluna", pergunta_exemplo, True)
    sessao.nova_conversa("aluna")
    assert banco.mensagens_da_sessao("aluna") == []
    assert len(banco.respostas_do_aluno("aluna")) == 1


def test_sessoes_nao_se_misturam():
    sessao.obter_sessao("ana").lembrar("user", "pergunta da Ana")
    assert sessao.obter_sessao("bia").historico == []


def test_correcao_deterministica_registra_no_banco(pergunta_exemplo):
    s = sessao.obter_sessao("aluna")
    simulado.iniciar(s, [pergunta_exemplo])
    texto = simulado.corrigir(s, "a")
    assert "Correto" in texto and "Fim do simulado" in texto
    assert banco.respostas_do_aluno("aluna")[0]["correta"] == 1


def test_embaralhar_mantem_a_resposta_certa(pergunta_exemplo):
    trecho = {"area": "Gestão e governança do Azure", "titulo": "Policy", "url": "https://x"}
    for _ in range(20):
        p = simulado._validar_e_embaralhar(dict(pergunta_exemplo), [trecho], None)
        assert p["alternativas"][p["correta"]] == "Azure Policy"


def test_pergunta_invalida_e_descartada():
    assert simulado._validar_e_embaralhar({"enunciado": "x", "alternativas": {"A": "1"}, "correta": "A"},
                                          [{"area": "a", "titulo": "t", "url": "u"}], None) is None
