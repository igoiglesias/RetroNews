from unittest.mock import patch, MagicMock

import pytest

from databases.models import Feed, Noticia
from services.feed import buscar_todos_feeds, processar_feed, atualizar_todos_feeds


@pytest.mark.anyio
async def test_buscar_todos_feeds_retorna_ativos():
    await Feed.create(nome="Feed Ativo", url_rss="https://a.com/rss", url_site="https://a.com", ativo=True)
    await Feed.create(nome="Feed Inativo", url_rss="https://b.com/rss", url_site="https://b.com", ativo=False)

    feeds = await buscar_todos_feeds()
    assert len(feeds) == 1
    assert feeds[0].nome == "Feed Ativo"


@pytest.mark.anyio
async def test_processar_feed_cria_noticias():
    feed = await Feed.create(nome="Test Feed", url_rss="https://test.com/rss", url_site="https://test.com")

    entrada_mock = MagicMock()
    entrada_mock.get.side_effect = lambda k, d=None: {
        "title": "Noticia 1",
        "link": "https://test.com/1",
        "summary": "<p>Resumo</p>",
        "author": "Autor",
    }.get(k, d)

    feed_parseado = MagicMock()
    feed_parseado.bozo = False
    feed_parseado.entries = [entrada_mock]

    with patch("services.feed.feedparser.parse", return_value=feed_parseado):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 1
    assert noticias[0].titulo == "Noticia 1"
    assert noticias[0].resumo_original == "Resumo"


@pytest.mark.anyio
async def test_processar_feed_ignora_duplicatas():
    feed = await Feed.create(nome="Test Feed", url_rss="https://test.com/rss", url_site="https://test.com")
    await Noticia.create(feed=feed, titulo="Existente", url="https://test.com/1", resumo_original="")

    entrada_mock = MagicMock()
    entrada_mock.get.side_effect = lambda k, d=None: {
        "title": "Existente",
        "link": "https://test.com/1",
        "summary": "Resumo",
    }.get(k, d)

    feed_parseado = MagicMock()
    feed_parseado.bozo = False
    feed_parseado.entries = [entrada_mock]

    with patch("services.feed.feedparser.parse", return_value=feed_parseado):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 1


@pytest.mark.anyio
async def test_processar_feed_ignora_entrada_sem_titulo():
    feed = await Feed.create(nome="Test Feed", url_rss="https://test.com/rss", url_site="https://test.com")

    entrada_mock = MagicMock()
    entrada_mock.get.side_effect = lambda k, d=None: {
        "link": "https://test.com/1",
        "summary": "Resumo",
    }.get(k, d)

    feed_parseado = MagicMock()
    feed_parseado.bozo = False
    feed_parseado.entries = [entrada_mock]

    with patch("services.feed.feedparser.parse", return_value=feed_parseado):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 0


@pytest.mark.anyio
async def test_processar_feed_ignora_entrada_sem_url():
    feed = await Feed.create(nome="Test Feed", url_rss="https://test.com/rss", url_site="https://test.com")

    entrada_mock = MagicMock()
    entrada_mock.get.side_effect = lambda k, d=None: {
        "title": "Titulo sem link",
        "summary": "Resumo",
    }.get(k, d)

    feed_parseado = MagicMock()
    feed_parseado.bozo = False
    feed_parseado.entries = [entrada_mock]

    with patch("services.feed.feedparser.parse", return_value=feed_parseado):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 0


@pytest.mark.anyio
async def test_processar_feed_trunca_autor_longo():
    feed = await Feed.create(nome="Test Feed", url_rss="https://test.com/rss", url_site="https://test.com")

    autor_longo = "A" * 250

    entrada_mock = MagicMock()
    entrada_mock.get.side_effect = lambda k, d=None: {
        "title": "Noticia com autor longo",
        "link": "https://test.com/autor-longo",
        "summary": "Resumo",
        "author": autor_longo,
    }.get(k, d)

    feed_parseado = MagicMock()
    feed_parseado.bozo = False
    feed_parseado.entries = [entrada_mock]

    with patch("services.feed.feedparser.parse", return_value=feed_parseado):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 1
    assert len(noticias[0].autor) <= 200
    assert noticias[0].autor.endswith("...")


@pytest.mark.anyio
async def test_processar_feed_erro_rede_nao_quebra():
    feed = await Feed.create(nome="Test Feed", url_rss="https://badurl.com/rss", url_site="https://badurl.com")

    with patch("services.feed.feedparser.parse", side_effect=Exception("Network error")):
        await processar_feed(feed)

    noticias = await Noticia.all()
    assert len(noticias) == 0


@pytest.mark.anyio
async def test_atualizar_todos_feeds_orquestra():
    await Feed.create(nome="Feed 1", url_rss="https://f1.com/rss", url_site="https://f1.com", ativo=True)

    with patch("services.feed.processar_feed") as mock_processar, \
         patch("services.feed.processar_noticias_pendentes") as mock_resumo, \
         patch("services.feed.invalidar_cache") as mock_cache:
        mock_processar.return_value = None
        mock_resumo.return_value = None
        await atualizar_todos_feeds()

    mock_processar.assert_called_once()
    mock_resumo.assert_called_once()
    mock_cache.assert_called_once()
