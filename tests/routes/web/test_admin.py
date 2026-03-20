from unittest.mock import patch

import pytest

from databases.models import Admin, Feed, Sugestao
from tools.seguranca import gerar_jwt, hash_senha


@pytest.fixture
async def admin_db():
    return await Admin.create(usuario="admin", senha_hash=hash_senha("senha123"))


@pytest.fixture
def admin_cookie():
    token = gerar_jwt("admin")
    return {"admin_jwt": token}


@pytest.mark.anyio
async def test_admin_login_page(cliente):
    resposta = await cliente.get("/admin/login")
    assert resposta.status_code == 200
    assert "usuario" in resposta.text
    assert "senha" in resposta.text


@pytest.mark.anyio
async def test_admin_login_invalido(cliente, admin_db):
    resposta = await cliente.post(
        "/admin/login",
        data={"usuario": "admin", "senha": "errada"},
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert "erro=1" in resposta.headers["location"]


@pytest.mark.anyio
async def test_admin_login_valido(cliente, admin_db):
    resposta = await cliente.post(
        "/admin/login",
        data={"usuario": "admin", "senha": "senha123"},
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert "/admin/dashboard" in resposta.headers["location"]
    assert "admin_jwt" in resposta.headers.get("set-cookie", "")


@pytest.mark.anyio
async def test_admin_sugestoes_sem_auth(cliente):
    resposta = await cliente.get("/admin/sugestoes", follow_redirects=False)
    assert resposta.status_code == 303
    assert "/admin/login" in resposta.headers["location"]


@pytest.mark.anyio
async def test_admin_sugestoes_com_jwt(cliente, admin_db, admin_cookie):
    resposta = await cliente.get("/admin/sugestoes", cookies=admin_cookie)
    assert resposta.status_code == 200
    assert "pendentes" in resposta.text


@pytest.mark.anyio
async def test_admin_sugestoes_jwt_invalido(cliente):
    resposta = await cliente.get(
        "/admin/sugestoes",
        cookies={"admin_jwt": "token.invalido.aqui"},
        follow_redirects=False,
    )
    assert resposta.status_code == 303


@pytest.mark.anyio
async def test_admin_aprovar(cliente, admin_db, admin_cookie):
    s = await Sugestao.create(nome_site="Blog", url_site="https://blog.com", status="pendente")

    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            f"/admin/sugestoes/{s.id}/aprovar",
            data={"csrf_token": "valid"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303

    await s.refresh_from_db()
    assert s.status == "aprovada"


@pytest.mark.anyio
async def test_admin_rejeitar(cliente, admin_db, admin_cookie):
    s = await Sugestao.create(nome_site="Spam", url_site="https://spam.com", status="pendente")

    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            f"/admin/sugestoes/{s.id}/rejeitar",
            data={"csrf_token": "valid"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303

    await s.refresh_from_db()
    assert s.status == "rejeitada"


@pytest.mark.anyio
async def test_admin_pagina_trocar_senha(cliente, admin_db, admin_cookie):
    resposta = await cliente.get("/admin/senha", cookies=admin_cookie)
    assert resposta.status_code == 200
    assert "senha_atual" in resposta.text


@pytest.mark.anyio
async def test_admin_trocar_senha_sucesso(cliente, admin_db, admin_cookie):
    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            "/admin/senha",
            data={
                "senha_atual": "senha123",
                "senha_nova": "novaSenha456",
                "senha_confirma": "novaSenha456",
                "csrf_token": "valid",
            },
            cookies=admin_cookie,
        )
    assert resposta.status_code == 200
    assert "sucesso" in resposta.text.lower() or "alterada" in resposta.text.lower()


@pytest.mark.anyio
async def test_admin_trocar_senha_atual_errada(cliente, admin_db, admin_cookie):
    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            "/admin/senha",
            data={
                "senha_atual": "errada",
                "senha_nova": "novaSenha456",
                "senha_confirma": "novaSenha456",
                "csrf_token": "valid",
            },
            cookies=admin_cookie,
        )
    assert resposta.status_code == 200
    assert "incorreta" in resposta.text.lower()


@pytest.mark.anyio
async def test_admin_trocar_senha_nao_coincide(cliente, admin_db, admin_cookie):
    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            "/admin/senha",
            data={
                "senha_atual": "senha123",
                "senha_nova": "novaSenha456",
                "senha_confirma": "outraSenha789",
                "csrf_token": "valid",
            },
            cookies=admin_cookie,
        )
    assert resposta.status_code == 200
    assert "coincidem" in resposta.text.lower()


@pytest.mark.anyio
async def test_admin_trocar_senha_curta(cliente, admin_db, admin_cookie):
    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            "/admin/senha",
            data={
                "senha_atual": "senha123",
                "senha_nova": "abc",
                "senha_confirma": "abc",
                "csrf_token": "valid",
            },
            cookies=admin_cookie,
        )
    assert resposta.status_code == 200
    assert "6 caracteres" in resposta.text.lower()


# ── Dashboard ──

@pytest.mark.anyio
async def test_admin_dashboard(cliente, admin_db, admin_cookie):
    resposta = await cliente.get("/admin/dashboard", cookies=admin_cookie)
    assert resposta.status_code == 200
    assert "dashboard" in resposta.text.lower()


@pytest.mark.anyio
async def test_admin_dashboard_sem_auth(cliente):
    resposta = await cliente.get("/admin/dashboard", follow_redirects=False)
    assert resposta.status_code == 303


# ── Feeds ──

@pytest.mark.anyio
async def test_admin_feeds_listar(cliente, admin_db, admin_cookie):
    await Feed.create(nome="Feed A", url_rss="https://a.com/rss", url_site="https://a.com")
    resposta = await cliente.get("/admin/feeds", cookies=admin_cookie)
    assert resposta.status_code == 200
    assert "Feed A" in resposta.text


@pytest.mark.anyio
async def test_admin_feeds_criar(cliente, admin_db, admin_cookie):
    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            "/admin/feeds/novo",
            data={"nome": "Novo Feed", "url_rss": "https://novo.com/rss", "url_site": "https://novo.com", "csrf_token": "v"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303
    assert await Feed.exists(url_rss="https://novo.com/rss")


@pytest.mark.anyio
async def test_admin_feeds_editar(cliente, admin_db, admin_cookie):
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")

    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            f"/admin/feeds/{feed.id}/editar",
            data={"nome": "B", "url_rss": "https://b.com/rss", "url_site": "https://b.com", "csrf_token": "v"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303
    await feed.refresh_from_db()
    assert feed.nome == "B"


@pytest.mark.anyio
async def test_admin_feeds_alternar(cliente, admin_db, admin_cookie):
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)

    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            f"/admin/feeds/{feed.id}/alternar",
            data={"csrf_token": "v"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303
    await feed.refresh_from_db()
    assert feed.ativo is False


@pytest.mark.anyio
async def test_admin_feeds_excluir(cliente, admin_db, admin_cookie):
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")

    with patch("routes.web.admin.validar_csrf_token", return_value=True):
        resposta = await cliente.post(
            f"/admin/feeds/{feed.id}/excluir",
            data={"csrf_token": "v"},
            cookies=admin_cookie,
            follow_redirects=False,
        )
    assert resposta.status_code == 303
    assert await Feed.exists(id=feed.id) is False
