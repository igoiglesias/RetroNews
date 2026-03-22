import pytest

from databases.models import Feed, Noticia, Tag
from services.noticia import (
    listar_noticias,
    listar_por_tag,
    listar_por_feed,
    listar_feeds,
    obter_status,
)


@pytest.mark.anyio
async def test_listar_noticias_retorna_paginado():
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    for i in range(25):
        await Noticia.create(
            feed=feed, titulo=f"N{i}", url=f"https://f.com/{i}",
            resumo_original="R", resumo_ia="Comentario",
        )

    dados = await listar_noticias(pagina=1)
    assert len(dados["noticias"]) == 20
    assert dados["pagina"] == 1
    assert dados["total_paginas"] == 2


@pytest.mark.anyio
async def test_listar_noticias_pagina_2():
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    for i in range(25):
        await Noticia.create(
            feed=feed, titulo=f"N{i}", url=f"https://f.com/{i}",
            resumo_original="R", resumo_ia="Comentario",
        )

    dados = await listar_noticias(pagina=2)
    assert len(dados["noticias"]) == 5
    assert dados["pagina"] == 2


@pytest.mark.anyio
async def test_listar_noticias_vazio():
    dados = await listar_noticias(pagina=1)
    assert dados["noticias"] == []
    assert dados["total_paginas"] == 1


@pytest.mark.anyio
async def test_listar_noticias_filtra_sem_ia():
    feed = await Feed.create(nome="F", url_rss="https://f2.com/rss", url_site="https://f2.com")
    await Noticia.create(feed=feed, titulo="Com IA", url="https://f2.com/1", resumo_original="R", resumo_ia="C")
    await Noticia.create(feed=feed, titulo="Sem IA", url="https://f2.com/2", resumo_original="R")

    dados = await listar_noticias(pagina=1)
    assert len(dados["noticias"]) == 1
    assert dados["noticias"][0].titulo == "Com IA"


@pytest.mark.anyio
async def test_listar_por_tag_existente():
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    tag = await Tag.create(nome="backend")
    noticia = await Noticia.create(
        feed=feed, titulo="N1", url="https://f.com/1",
        resumo_original="R", resumo_ia="Comentario",
    )
    await noticia.tags.add(tag)

    dados = await listar_por_tag(nome="backend", pagina=1)
    assert len(dados["noticias"]) == 1
    assert dados["nome_tag"] == "backend"


@pytest.mark.anyio
async def test_listar_por_tag_inexistente():
    dados = await listar_por_tag(nome="naoexiste", pagina=1)
    assert dados["noticias"] == []


@pytest.mark.anyio
async def test_listar_por_feed_existente():
    feed = await Feed.create(nome="Meu Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(
        feed=feed, titulo="N1", url="https://f.com/1",
        resumo_original="R", resumo_ia="Comentario",
    )

    dados = await listar_por_feed(feed_id=feed.id, pagina=1)
    assert dados is not None
    assert len(dados["noticias"]) == 1
    assert dados["nome_feed"] == "Meu Feed"


@pytest.mark.anyio
async def test_listar_por_feed_inexistente():
    dados = await listar_por_feed(feed_id=9999, pagina=1)
    assert dados is None


@pytest.mark.anyio
async def test_listar_feeds():
    await Feed.create(nome="A Feed", url_rss="https://a.com/rss", url_site="https://a.com")
    await Feed.create(nome="B Feed", url_rss="https://b.com/rss", url_site="https://b.com")

    dados = await listar_feeds()
    assert len(dados["feeds"]) == 2


@pytest.mark.anyio
async def test_obter_status_vazio():
    dados = await obter_status()
    assert dados["total_feeds"] == 0
    assert dados["total_noticias"] == 0
    assert dados["ultima_atualizacao"] is None


@pytest.mark.anyio
async def test_obter_status_com_dados():
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(feed=feed, titulo="N", url="https://f.com/1", resumo_original="R")

    dados = await obter_status()
    assert dados["total_feeds"] == 1
    assert dados["total_noticias"] == 1
    assert dados["ultima_atualizacao"] is not None
