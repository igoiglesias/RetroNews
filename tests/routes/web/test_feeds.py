import pytest

from databases.models import Feed


@pytest.mark.anyio
async def test_feeds_retorna_200(cliente):
    resposta = await cliente.get("/feeds")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_feeds_mostra_feeds(cliente):
    await Feed.create(nome="Meu Feed", url_rss="https://mf.com/rss", url_site="https://mf.com")

    resposta = await cliente.get("/feeds")
    assert "Meu Feed" in resposta.text


@pytest.mark.anyio
async def test_feeds_sem_feeds(cliente):
    resposta = await cliente.get("/feeds")
    assert "Nenhum feed cadastrado" in resposta.text
