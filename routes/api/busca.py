from fastapi import APIRouter, Query, Request

from bootstrap import templates
from services.busca import buscar_noticias

router = APIRouter(prefix="/api")


@router.get("/busca")
async def api_busca(request: Request, q: str = Query(""), pagina: int = Query(1, ge=1)):
    if not q.strip():
        return templates.TemplateResponse(
            request, "partials/noticias_lista.html",
            context={"noticias": [], "pagina": 1, "total_paginas": 1, "termo": "", "buscando": False},
        )

    dados = await buscar_noticias(q, pagina=pagina)
    dados["buscando"] = True
    return templates.TemplateResponse(request, "partials/noticias_lista.html", context=dados)
