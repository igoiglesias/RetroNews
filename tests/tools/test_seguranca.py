from unittest.mock import patch

from tools.seguranca import (
    detectar_spam,
    gerar_csrf_token,
    gerar_jwt,
    hash_senha,
    validar_csrf_token,
    validar_jwt,
    verificar_senha,
)


def test_csrf_token_valido():
    token = gerar_csrf_token("sessao1")
    assert validar_csrf_token(token, "sessao1") is True


def test_csrf_token_sessao_errada():
    token = gerar_csrf_token("sessao1")
    assert validar_csrf_token(token, "sessao2") is False


def test_csrf_token_vazio():
    assert validar_csrf_token("", "sessao1") is False
    assert validar_csrf_token(None, "sessao1") is False


def test_csrf_token_formato_invalido():
    assert validar_csrf_token("invalido", "sessao1") is False


def test_csrf_token_expirado():
    with patch("tools.seguranca.time") as mock_time:
        mock_time.time.return_value = 1000000
        token = gerar_csrf_token("sessao1")
        mock_time.time.return_value = 1000000 + 3601
        assert validar_csrf_token(token, "sessao1") is False


def test_hash_e_verificar_senha():
    h = hash_senha("minha_senha_123")
    assert verificar_senha("minha_senha_123", h) is True
    assert verificar_senha("senha_errada", h) is False


def test_jwt_valido():
    token = gerar_jwt("admin")
    usuario = validar_jwt(token)
    assert usuario == "admin"


def test_jwt_invalido():
    assert validar_jwt("token.invalido.aqui") is None
    assert validar_jwt("") is None


def test_jwt_expirado():
    with patch("tools.seguranca.JWT_EXPIRA_HORAS", 0):
        token = gerar_jwt("admin")
    # token com 0 horas de expiração — já expirou
    import time
    time.sleep(1)
    assert validar_jwt(token) is None


def test_detectar_spam_links_excessivos():
    assert detectar_spam("veja http://a.com http://b.com http://c.com http://d.com") is True


def test_detectar_spam_palavras_proibidas():
    assert detectar_spam("buy now este site") is True
    assert detectar_spam("free money here") is True


def test_detectar_spam_texto_normal():
    assert detectar_spam("Blog legal sobre Python e FastAPI") is False


def test_detectar_spam_texto_curto():
    assert detectar_spam("ab") is True


def test_detectar_spam_texto_vazio():
    assert detectar_spam("") is False
