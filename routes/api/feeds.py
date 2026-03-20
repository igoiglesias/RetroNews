import asyncio
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config.config import APP_DEBUG
from services.feed import atualizar_todos_feeds

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

_atualizando = False


@router.post("/feeds/atualizar")
async def atualizar_feeds():
    global _atualizando

    if not APP_DEBUG:
        return JSONResponse({"erro": "Endpoint disponivel apenas em modo debug"}, status_code=403)

    if _atualizando:
        return {"status": "em_andamento", "mensagem": "Atualizacao ja em andamento"}

    async def _executar():
        global _atualizando
        _atualizando = True
        try:
            await atualizar_todos_feeds()
            logger.info("Atualizacao em background concluida")
        except Exception as e:
            logger.error("Erro na atualizacao em background: %s", e, exc_info=True)
        finally:
            _atualizando = False

    asyncio.create_task(_executar())
    return {"status": "ok", "mensagem": "Atualizacao iniciada em background"}
