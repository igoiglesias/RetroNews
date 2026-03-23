import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import Response
from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from config.config import APP_DEBUG, APP_TITLE, LOG_LEVEL, RATE_LIMIT
from databases.db import TORTOISE_ORM

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        from services.busca import criar_indice_fts, reindexar_noticias
        from services.config_ia import inicializar_config_ia
        from services.scheduler import iniciar_scheduler

        FastAPICache.init(InMemoryBackend())

        # WAL mode para leitura concorrente no SQLite
        conn = Tortoise.get_connection("default")
        await conn.execute_script("PRAGMA journal_mode=WAL;")

        await criar_indice_fts()
        await reindexar_noticias()
        await inicializar_config_ia()

        scheduler = iniciar_scheduler()
        yield
        if scheduler:
            scheduler.shutdown()


app = FastAPI(
    title=APP_TITLE,
    lifespan=lifespan,
    docs_url="/docs" if APP_DEBUG else None,
    redoc_url=None,
    openapi_url="/openapi.json" if APP_DEBUG else None,
)

app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            request, "pages/erro.html",
            context={"mensagem": "Muitas requisicoes. Aguarde um momento."},
            status_code=429,
        )
    return JSONResponse({"erro": "Rate limit excedido"}, status_code=429)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=604800, immutable"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

FUSO_BR = ZoneInfo("America/Sao_Paulo")


def _data_br(valor: datetime | None, fmt: str = "%d/%m/%Y %H:%M") -> str:
    if valor is None:
        return ""
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=ZoneInfo("UTC"))
    return valor.astimezone(FUSO_BR).strftime(fmt)


templates.env.filters["data_br"] = _data_br

from config.config import SITE_URL
templates.env.globals["site_url"] = SITE_URL
