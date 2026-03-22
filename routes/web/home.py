from fastapi import APIRouter, Query, Request

from bootstrap import templates
from services.busca import buscar_noticias
from services.noticia import listar_noticias

router = APIRouter()


@router.get("/")
async def index(
    request: Request,
    pagina: int = Query(1, ge=1),
    q: str = Query(""),
):
    if q.strip():
        dados = await buscar_noticias(q, pagina=pagina)
        dados["buscando"] = True
    else:
        dados = await listar_noticias(pagina=pagina)
        dados["buscando"] = False
    dados["termo"] = q
    return templates.TemplateResponse(request, "pages/index.html", context=dados)
