from fastapi import APIRouter, Query, Request

from bootstrap import templates
from services.noticia import listar_noticias

router = APIRouter()


@router.get("/")
async def index(request: Request, pagina: int = Query(1, ge=1)):
    dados = await listar_noticias(pagina=pagina)
    return templates.TemplateResponse(request, "pages/index.html", context=dados)
