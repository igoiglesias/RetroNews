import pytest

from databases.models import Feed, Noticia


@pytest.mark.anyio
async def test_status_retorna_200(cliente):
    resposta = await cliente.get("/api/status")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_status_campos(cliente):
    resposta = await cliente.get("/api/status")
    dados = resposta.json()
    assert "total_feeds" in dados
    assert "total_noticias" in dados
    assert "ultima_atualizacao" in dados


@pytest.mark.anyio
async def test_status_com_dados(cliente):
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(feed=feed, titulo="N", url="https://f.com/1", resumo_original="R")

    resposta = await cliente.get("/api/status")
    dados = resposta.json()
    assert dados["total_feeds"] == 1
    assert dados["total_noticias"] == 1
    assert dados["ultima_atualizacao"] is not None
