from fastapi import APIRouter, Query, Request

from bootstrap import templates
from services.busca import buscar_noticias

router = APIRouter()


@router.get("/busca")
async def busca(request: Request, q: str = Query(""), pagina: int = Query(1, ge=1)):
    if not q.strip():
        return templates.TemplateResponse(
            request, "pages/busca.html",
            context={"noticias": [], "pagina": 1, "total_paginas": 1, "termo": ""},
        )

    dados = await buscar_noticias(q, pagina=pagina)
    return templates.TemplateResponse(request, "pages/busca.html", context=dados)
