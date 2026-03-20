from fastapi import APIRouter

from services.noticia import obter_status

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return await obter_status()
