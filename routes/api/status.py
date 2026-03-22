from fastapi import APIRouter

from services.noticia import obter_status

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    dados = await obter_status()
    ua = dados["ultima_atualizacao"]
    dados["ultima_atualizacao"] = ua.isoformat() if ua else None
    return dados
