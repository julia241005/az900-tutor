"""Senha (HTTP Basic) e limite de mensagens por minuto."""
import base64

import seguranca


def _basic(usuario, senha):
    return "Basic " + base64.b64encode(f"{usuario}:{senha}".encode()).decode()


def test_sem_senha_configurada_libera(monkeypatch):
    monkeypatch.setattr(seguranca, "SENHA", "")
    assert seguranca.senha_ok(None)


def test_senha_certa_e_errada(monkeypatch):
    monkeypatch.setattr(seguranca, "SENHA", "estudar900")
    assert seguranca.senha_ok(_basic("julia", "estudar900"))
    assert not seguranca.senha_ok(_basic("julia", "errada"))
    assert not seguranca.senha_ok(None)
    assert not seguranca.senha_ok("Basic isso-nao-e-base64!!")


def test_limitador_bloqueia_acima_do_limite_e_libera_depois_da_janela():
    lim = seguranca.LimitadorDeTaxa(limite=3, janela_segundos=60)
    assert all(lim.permitir("1.2.3.4", agora=t) for t in (0, 1, 2))
    assert not lim.permitir("1.2.3.4", agora=3)       # 4ª mensagem no mesmo minuto
    assert lim.permitir("5.6.7.8", agora=3)           # outro IP não é afetado
    assert lim.permitir("1.2.3.4", agora=61)          # passou a janela da 1ª mensagem
