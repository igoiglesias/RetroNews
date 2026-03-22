import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import SCHEDULER_INTERVALO_MINUTOS

logger = logging.getLogger(__name__)


async def limpar_logs_antigos() -> None:
    from databases.models import LogProcessamento
    limite = datetime.now() - timedelta(days=7)
    deletados = await LogProcessamento.filter(criado_em__lt=limite).delete()
    if deletados:
        logger.info("Removidos %d logs antigos", deletados)


async def otimizar_banco() -> None:
    from tortoise import Tortoise
    conn = Tortoise.get_connection("default")
    await conn.execute_script("PRAGMA optimize;")
    logger.info("PRAGMA optimize executado")


def iniciar_scheduler() -> AsyncIOScheduler | None:
    if os.getenv("RETRONEWS_DISABLE_SCHEDULER"):
        logger.info("Scheduler desativado via RETRONEWS_DISABLE_SCHEDULER")
        return None

    from services.feed import atualizar_todos_feeds

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        atualizar_todos_feeds,
        "interval",
        minutes=SCHEDULER_INTERVALO_MINUTOS,
        id="atualizar_feeds",
        name="Atualizar todos os feeds RSS",
    )
    scheduler.add_job(
        limpar_logs_antigos,
        "interval",
        hours=24,
        id="limpar_logs",
        name="Limpar logs com mais de 7 dias",
    )
    scheduler.add_job(
        otimizar_banco,
        "interval",
        hours=24,
        id="otimizar_banco",
        name="PRAGMA optimize",
    )
    scheduler.start()
    logger.info(
        "Scheduler iniciado — atualizacao a cada %d minutos",
        SCHEDULER_INTERVALO_MINUTOS,
    )
    return scheduler
