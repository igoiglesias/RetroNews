import os

os.environ["RETRONEWS_DISABLE_SCHEDULER"] = "1"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app import app
from tools.cache import invalidar_cache


@pytest_asyncio.fixture(autouse=True)
async def _inicializa_banco(tmp_path):
    invalidar_cache()

    db_file = tmp_path / "test.db"
    db_url = f"sqlite://{db_file}"

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["databases.models"]},
        _enable_global_fallback=True,
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def cliente():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
