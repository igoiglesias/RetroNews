import pytest

from databases.models import Feed, Noticia


@pytest.mark.anyio
async def test_index_retorna_200(cliente):
    resposta = await cliente.get("/")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_index_contem_html(cliente):
    resposta = await cliente.get("/")
    assert "text/html" in resposta.headers["content-type"]


@pytest.mark.anyio
async def test_index_contem_titulo(cliente):
    resposta = await cliente.get("/")
    assert "RetroNews" in resposta.text


@pytest.mark.anyio
async def test_index_mostra_noticias(cliente):
    feed = await Feed.create(nome="Test", url_rss="https://t.com/rss", url_site="https://t.com")
    await Noticia.create(feed=feed, titulo="Noticia Teste", url="https://t.com/1", resumo_original="Resumo")

    resposta = await cliente.get("/")
    assert "Noticia Teste" in resposta.text


@pytest.mark.anyio
async def test_index_paginacao(cliente):
    feed = await Feed.create(nome="Test", url_rss="https://t.com/rss", url_site="https://t.com")
    for i in range(25):
        await Noticia.create(feed=feed, titulo=f"N{i}", url=f"https://t.com/{i}", resumo_original="R")

    resposta = await cliente.get("/?pagina=2")
    assert resposta.status_code == 200
    assert "pagina 2" in resposta.text


@pytest.mark.anyio
async def test_index_sem_noticias(cliente):
    resposta = await cliente.get("/")
    assert "Nenhuma noticia encontrada" in resposta.text
