import pytest

from databases.models import Feed, Noticia
from services.admin_feed import (
    alternar_feed,
    atualizar_feed,
    criar_feed,
    excluir_feed,
    listar_feeds_admin,
    obter_feed,
)


@pytest.mark.anyio
async def test_listar_feeds_admin_todos():
    await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)
    await Feed.create(nome="B", url_rss="https://b.com/rss", url_site="https://b.com", ativo=False)

    dados = await listar_feeds_admin()
    assert len(dados["feeds"]) == 2


@pytest.mark.anyio
async def test_listar_feeds_admin_filtro_ativos():
    await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)
    await Feed.create(nome="B", url_rss="https://b.com/rss", url_site="https://b.com", ativo=False)

    dados = await listar_feeds_admin(filtro="ativos")
    assert len(dados["feeds"]) == 1
    assert dados["feeds"][0].nome == "A"


@pytest.mark.anyio
async def test_listar_feeds_admin_filtro_inativos():
    await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)
    await Feed.create(nome="B", url_rss="https://b.com/rss", url_site="https://b.com", ativo=False)

    dados = await listar_feeds_admin(filtro="inativos")
    assert len(dados["feeds"]) == 1
    assert dados["feeds"][0].nome == "B"


@pytest.mark.anyio
async def test_listar_feeds_conta_noticias():
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")
    await Noticia.create(feed=feed, titulo="N1", url="https://a.com/1", resumo_original="R")
    await Noticia.create(feed=feed, titulo="N2", url="https://a.com/2", resumo_original="R")

    dados = await listar_feeds_admin()
    assert dados["feeds"][0].total_noticias == 2


@pytest.mark.anyio
async def test_obter_feed():
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")
    assert await obter_feed(feed.id) is not None
    assert await obter_feed(999) is None


@pytest.mark.anyio
async def test_atualizar_feed():
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")
    resultado = await atualizar_feed(feed.id, "Novo Nome", "https://novo.com/rss", "https://novo.com")
    assert resultado is True

    await feed.refresh_from_db()
    assert feed.nome == "Novo Nome"
    assert feed.url_rss == "https://novo.com/rss"


@pytest.mark.anyio
async def test_atualizar_feed_inexistente():
    assert await atualizar_feed(999, "X", "X", "X") is False


@pytest.mark.anyio
async def test_alternar_feed():
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)

    await alternar_feed(feed.id)
    await feed.refresh_from_db()
    assert feed.ativo is False

    await alternar_feed(feed.id)
    await feed.refresh_from_db()
    assert feed.ativo is True


@pytest.mark.anyio
async def test_alternar_feed_inexistente():
    assert await alternar_feed(999) is False


@pytest.mark.anyio
async def test_excluir_feed_com_noticias():
    feed = await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")
    await Noticia.create(feed=feed, titulo="N1", url="https://a.com/1", resumo_original="R")

    resultado = await excluir_feed(feed.id)
    assert resultado is True
    assert await Feed.exists(id=feed.id) is False
    assert await Noticia.filter(url="https://a.com/1").count() == 0


@pytest.mark.anyio
async def test_excluir_feed_inexistente():
    assert await excluir_feed(999) is False


@pytest.mark.anyio
async def test_criar_feed():
    feed = await criar_feed("Novo", "https://novo.com/rss", "https://novo.com")
    assert feed is not None
    assert feed.nome == "Novo"


@pytest.mark.anyio
async def test_criar_feed_duplicado():
    await Feed.create(nome="A", url_rss="https://a.com/rss", url_site="https://a.com")
    feed = await criar_feed("B", "https://a.com/rss", "https://a.com")
    assert feed is None
