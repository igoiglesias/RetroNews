import warnings

import pytest_asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from tortoise import Tortoise
from tortoise.warnings import TortoiseLoopSwitchWarning

from tools.cache import invalidar_cache


@pytest_asyncio.fixture(autouse=True)
async def _inicializa_banco(anyio_backend, tmp_path):
    db_file = tmp_path / "test.db"
    db_url = f"sqlite://{db_file}"

    FastAPICache.init(InMemoryBackend())
    await invalidar_cache()

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["databases.models"]},
        _enable_global_fallback=True,
    )
    await Tortoise.generate_schemas()

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=TortoiseLoopSwitchWarning)
        yield

    await Tortoise.close_connections()
