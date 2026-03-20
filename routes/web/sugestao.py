from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from bootstrap import templates
from databases.models import Feed, Sugestao
from services.sugestao import criar_sugestao
from tools.seguranca import detectar_spam, gerar_csrf_token, obter_ip, validar_csrf_token

router = APIRouter()


@router.get("/sugerir")
async def formulario_sugestao(request: Request):
    session_id = obter_ip(request)
    csrf_token = gerar_csrf_token(session_id)
    return templates.TemplateResponse(
        request, "pages/sugerir.html",
        context={"csrf_token": csrf_token},
    )


@router.post("/sugerir")
async def enviar_sugestao(
    request: Request,
    nome_site: str = Form(...),
    url_site: str = Form(...),
    url_rss: str = Form(""),
    motivo: str = Form(""),
    csrf_token: str = Form(...),
    honeypot: str = Form(""),
):
    session_id = obter_ip(request)
    erro = None

    # honeypot — bots preenchem campos ocultos
    if honeypot:
        return RedirectResponse("/sugerir?ok=1", status_code=303)

    if not validar_csrf_token(csrf_token, session_id):
        erro = "Sessao expirada. Tente novamente."
    elif not nome_site.strip() or not url_site.strip():
        erro = "Nome e URL do site sao obrigatorios."
    elif not url_site.strip().startswith(("http://", "https://")):
        erro = "URL deve comecar com http:// ou https://"
    elif detectar_spam(nome_site) or detectar_spam(motivo):
        erro = "Conteudo detectado como spam."

    if not erro and url_rss.strip():
        if await Feed.exists(url_rss=url_rss.strip()):
            erro = "Esse feed RSS ja esta cadastrado na plataforma."
        elif await Sugestao.exists(url_rss=url_rss.strip(), status="pendente"):
            erro = "Esse feed RSS ja foi sugerido e esta aguardando aprovacao."

    if not erro and url_site.strip():
        if await Feed.exists(url_site=url_site.strip()):
            erro = "Esse site ja esta cadastrado na plataforma."

    if erro:
        csrf_novo = gerar_csrf_token(session_id)
        return templates.TemplateResponse(
            request, "pages/sugerir.html",
            context={
                "csrf_token": csrf_novo,
                "erro": erro,
                "nome_site": nome_site,
                "url_site": url_site,
                "url_rss": url_rss,
                "motivo": motivo,
            },
        )

    ip = obter_ip(request)
    await criar_sugestao(nome_site, url_site, url_rss, motivo, ip)
    return RedirectResponse("/sugerir?ok=1", status_code=303)
