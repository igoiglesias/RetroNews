from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from bootstrap import templates
from services.noticia import listar_por_feed

router = APIRouter()


@router.get("/feed/{feed_id}")
async def feed(request: Request, feed_id: int, pagina: int = Query(1, ge=1)):
    dados = await listar_por_feed(feed_id=feed_id, pagina=pagina)
    if dados is None:
        return HTMLResponse("Feed nao encontrado", status_code=404)
    return templates.TemplateResponse(request, "pages/feed.html", context=dados)
