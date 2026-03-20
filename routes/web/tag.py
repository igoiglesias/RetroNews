from fastapi import APIRouter, Query, Request

from bootstrap import templates
from services.noticia import listar_por_tag

router = APIRouter()


@router.get("/tag/{nome}")
async def tag(request: Request, nome: str, pagina: int = Query(1, ge=1)):
    dados = await listar_por_tag(nome=nome, pagina=pagina)
    return templates.TemplateResponse(request, "pages/tag.html", context=dados)
