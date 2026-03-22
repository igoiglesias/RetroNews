import pytest

from databases.models import Feed, Noticia


@pytest.mark.anyio
async def test_feed_retorna_200(cliente):
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    resposta = await cliente.get(f"/feed/{feed.id}")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_feed_mostra_noticias(cliente):
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(
        feed=feed, titulo="Post Feed", url="https://f.com/1",
        resumo_original="R", resumo_ia="Comentario IA",
    )

    resposta = await cliente.get(f"/feed/{feed.id}")
    assert "Post Feed" in resposta.text


@pytest.mark.anyio
async def test_feed_inexistente_404(cliente):
    resposta = await cliente.get("/feed/9999")
    assert resposta.status_code == 404
