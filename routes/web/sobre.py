from fastapi import APIRouter, Request

from bootstrap import templates

router = APIRouter()


@router.get("/sobre")
async def sobre(request: Request):
    return templates.TemplateResponse(request, "pages/sobre.html")
