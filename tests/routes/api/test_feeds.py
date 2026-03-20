import asyncio
from unittest.mock import AsyncMock, patch

import pytest

import routes.api.feeds as feeds_module


@pytest.fixture(autouse=True)
def _reset_atualizando():
    feeds_module._atualizando = False
    yield
    feeds_module._atualizando = False


@pytest.mark.anyio
async def test_atualizar_feeds_em_debug(cliente):
    mock_atualizar = AsyncMock()
    with patch("routes.api.feeds.APP_DEBUG", True), \
         patch("routes.api.feeds.atualizar_todos_feeds", mock_atualizar):
        resposta = await cliente.post("/api/feeds/atualizar")
        await asyncio.sleep(0.1)

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"
    mock_atualizar.assert_called_once()


@pytest.mark.anyio
async def test_atualizar_feeds_fora_debug(cliente):
    with patch("routes.api.feeds.APP_DEBUG", False):
        resposta = await cliente.post("/api/feeds/atualizar")

    assert resposta.status_code == 403


@pytest.mark.anyio
async def test_atualizar_feeds_ja_em_andamento(cliente):
    feeds_module._atualizando = True
    with patch("routes.api.feeds.APP_DEBUG", True):
        resposta = await cliente.post("/api/feeds/atualizar")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "em_andamento"
