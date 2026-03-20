import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import SCHEDULER_INTERVALO_MINUTOS

logger = logging.getLogger(__name__)


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
    scheduler.start()
    logger.info(
        "Scheduler iniciado — atualizacao a cada %d minutos",
        SCHEDULER_INTERVALO_MINUTOS,
    )
    return scheduler
