import asyncio

from fastapi import APIRouter, Cookie, Form, Query, Request
from fastapi.responses import RedirectResponse

from bootstrap import templates
from services.admin import autenticar, obter_admin, trocar_senha
from services.admin_feed import (
    alternar_feed,
    atualizar_feed,
    criar_feed,
    excluir_feed,
    listar_feeds_admin,
    obter_feed,
)
from services.feed import atualizar_todos_feeds
from services.noticia import obter_status
from services.sugestao import aprovar_sugestao, contar_pendentes, listar_sugestoes, rejeitar_sugestao
from tools.seguranca import gerar_csrf_token, gerar_jwt, validar_csrf_token, validar_jwt

router = APIRouter(prefix="/admin")


async def _obter_admin_logado(admin_jwt: str | None) -> str | None:
    if not admin_jwt:
        return None
    usuario = validar_jwt(admin_jwt)
    if not usuario:
        return None
    admin = await obter_admin(usuario)
    if not admin:
        return None
    return usuario


def _redirecionar_login():
    return RedirectResponse("/admin/login", status_code=303)


# ── Auth ──

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "pages/admin_login.html")


@router.post("/login")
async def login(usuario: str = Form(...), senha: str = Form(...)):
    admin = await autenticar(usuario, senha)
    if not admin:
        return RedirectResponse("/admin/login?erro=1", status_code=303)

    token = gerar_jwt(admin.usuario)
    response = RedirectResponse("/admin/dashboard", status_code=303)
    response.set_cookie(
        "admin_jwt", token,
        httponly=True, samesite="strict", max_age=3600 * 8,
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("admin_jwt")
    return response


# ── Dashboard ──

@router.get("/dashboard")
async def dashboard(request: Request, admin_jwt: str | None = Cookie(None)):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    stats = await obter_status()
    pendentes = await contar_pendentes()
    csrf = gerar_csrf_token(usuario)

    return templates.TemplateResponse(
        request, "pages/admin_dashboard.html",
        context={**stats, "pendentes": pendentes, "csrf_token": csrf, "usuario": usuario},
    )


@router.post("/atualizar-feeds")
async def forcar_atualizacao(
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/dashboard?erro=csrf", status_code=303)

    asyncio.create_task(atualizar_todos_feeds())
    return RedirectResponse("/admin/dashboard?msg=atualizacao", status_code=303)


# ── Feeds ──

@router.get("/feeds")
async def painel_feeds(
    request: Request,
    filtro: str = Query("todos"),
    pagina: int = Query(1, ge=1),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    dados = await listar_feeds_admin(pagina=pagina, filtro=filtro)
    csrf = gerar_csrf_token(usuario)

    return templates.TemplateResponse(
        request, "pages/admin_feeds.html",
        context={**dados, "csrf_token": csrf, "usuario": usuario},
    )


@router.get("/feeds/novo")
async def formulario_novo_feed(request: Request, admin_jwt: str | None = Cookie(None)):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    csrf = gerar_csrf_token(usuario)
    return templates.TemplateResponse(
        request, "pages/admin_feed_form.html",
        context={"csrf_token": csrf, "usuario": usuario, "feed": None},
    )


@router.post("/feeds/novo")
async def criar_novo_feed(
    request: Request,
    nome: str = Form(...),
    url_rss: str = Form(...),
    url_site: str = Form(...),
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/feeds?erro=csrf", status_code=303)

    feed = await criar_feed(nome, url_rss, url_site)
    if not feed:
        csrf = gerar_csrf_token(usuario)
        return templates.TemplateResponse(
            request, "pages/admin_feed_form.html",
            context={
                "csrf_token": csrf, "usuario": usuario, "feed": None,
                "erro": "Feed com essa URL RSS ja existe.",
                "nome": nome, "url_rss": url_rss, "url_site": url_site,
            },
        )

    return RedirectResponse("/admin/feeds?msg=criado", status_code=303)


@router.get("/feeds/{feed_id}/editar")
async def formulario_editar_feed(
    request: Request, feed_id: int, admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    feed = await obter_feed(feed_id)
    if not feed:
        return RedirectResponse("/admin/feeds", status_code=303)

    csrf = gerar_csrf_token(usuario)
    return templates.TemplateResponse(
        request, "pages/admin_feed_form.html",
        context={"csrf_token": csrf, "usuario": usuario, "feed": feed},
    )


@router.post("/feeds/{feed_id}/editar")
async def salvar_feed(
    request: Request,
    feed_id: int,
    nome: str = Form(...),
    url_rss: str = Form(...),
    url_site: str = Form(...),
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/feeds?erro=csrf", status_code=303)

    await atualizar_feed(feed_id, nome, url_rss, url_site)
    return RedirectResponse("/admin/feeds?msg=salvo", status_code=303)


@router.post("/feeds/{feed_id}/alternar")
async def alternar_status_feed(
    feed_id: int,
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/feeds?erro=csrf", status_code=303)

    await alternar_feed(feed_id)
    return RedirectResponse("/admin/feeds", status_code=303)


@router.post("/feeds/{feed_id}/excluir")
async def excluir_feed_route(
    feed_id: int,
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/feeds?erro=csrf", status_code=303)

    await excluir_feed(feed_id)
    return RedirectResponse("/admin/feeds?msg=excluido", status_code=303)


# ── Sugestoes ──

@router.get("/sugestoes")
async def painel_sugestoes(
    request: Request,
    status: str = Query("pendente"),
    pagina: int = Query(1, ge=1),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    dados = await listar_sugestoes(status=status, pagina=pagina)
    pendentes = await contar_pendentes()
    csrf = gerar_csrf_token(usuario)

    return templates.TemplateResponse(
        request, "pages/admin_sugestoes.html",
        context={**dados, "pendentes": pendentes, "csrf_token": csrf, "usuario": usuario},
    )


@router.post("/sugestoes/{sugestao_id}/aprovar")
async def aprovar(
    sugestao_id: int,
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/sugestoes?erro=csrf", status_code=303)

    await aprovar_sugestao(sugestao_id)
    return RedirectResponse("/admin/sugestoes", status_code=303)


@router.post("/sugestoes/{sugestao_id}/rejeitar")
async def rejeitar(
    sugestao_id: int,
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    if not validar_csrf_token(csrf_token, usuario):
        return RedirectResponse("/admin/sugestoes?erro=csrf", status_code=303)

    await rejeitar_sugestao(sugestao_id)
    return RedirectResponse("/admin/sugestoes", status_code=303)


# ── Senha ──

@router.get("/senha")
async def pagina_trocar_senha(
    request: Request,
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    csrf = gerar_csrf_token(usuario)
    return templates.TemplateResponse(
        request, "pages/admin_senha.html",
        context={"csrf_token": csrf, "usuario": usuario},
    )


@router.post("/senha")
async def trocar_senha_post(
    request: Request,
    senha_atual: str = Form(...),
    senha_nova: str = Form(...),
    senha_confirma: str = Form(...),
    csrf_token: str = Form(...),
    admin_jwt: str | None = Cookie(None),
):
    usuario = await _obter_admin_logado(admin_jwt)
    if not usuario:
        return _redirecionar_login()

    erro = None

    if not validar_csrf_token(csrf_token, usuario):
        erro = "Sessao expirada. Tente novamente."
    elif len(senha_nova) < 6:
        erro = "A nova senha deve ter pelo menos 6 caracteres."
    elif senha_nova != senha_confirma:
        erro = "As senhas nao coincidem."
    else:
        sucesso = await trocar_senha(usuario, senha_atual, senha_nova)
        if not sucesso:
            erro = "Senha atual incorreta."

    csrf = gerar_csrf_token(usuario)

    if erro:
        return templates.TemplateResponse(
            request, "pages/admin_senha.html",
            context={"csrf_token": csrf, "usuario": usuario, "erro": erro},
        )

    return templates.TemplateResponse(
        request, "pages/admin_senha.html",
        context={"csrf_token": csrf, "usuario": usuario, "sucesso": True},
    )
