from fastapi import APIRouter, Request

from bootstrap import templates
from services.noticia import listar_feeds

router = APIRouter()


@router.get("/feeds")
async def feeds(request: Request):
    dados = await listar_feeds()
    return templates.TemplateResponse(request, "pages/feeds.html", context=dados)
