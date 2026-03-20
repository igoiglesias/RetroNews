import math

from databases.models import Feed, Noticia

ITENS_POR_PAGINA = 20


async def listar_feeds_admin(pagina: int = 1, filtro: str = "todos") -> dict:
    if filtro == "ativos":
        query = Feed.filter(ativo=True)
    elif filtro == "inativos":
        query = Feed.filter(ativo=False)
    else:
        query = Feed.all()

    total = await query.count()
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    feeds = await query.order_by("nome").offset(offset).limit(ITENS_POR_PAGINA)

    # contar noticias por feed
    for feed in feeds:
        feed.total_noticias = await Noticia.filter(feed=feed).count()

    return {
        "feeds": feeds,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "filtro": filtro,
    }


async def obter_feed(feed_id: int) -> Feed | None:
    return await Feed.get_or_none(id=feed_id)


async def atualizar_feed(feed_id: int, nome: str, url_rss: str, url_site: str) -> bool:
    feed = await Feed.get_or_none(id=feed_id)
    if not feed:
        return False

    feed.nome = nome.strip()[:200]
    feed.url_rss = url_rss.strip()[:500]
    feed.url_site = url_site.strip()[:500]
    await feed.save()
    return True


async def alternar_feed(feed_id: int) -> bool:
    feed = await Feed.get_or_none(id=feed_id)
    if not feed:
        return False

    feed.ativo = not feed.ativo
    await feed.save()
    return True


async def excluir_feed(feed_id: int) -> bool:
    feed = await Feed.get_or_none(id=feed_id)
    if not feed:
        return False

    await Noticia.filter(feed=feed).delete()
    await feed.delete()
    return True


async def criar_feed(nome: str, url_rss: str, url_site: str) -> Feed | None:
    existe = await Feed.exists(url_rss=url_rss.strip())
    if existe:
        return None

    return await Feed.create(
        nome=nome.strip()[:200],
        url_rss=url_rss.strip()[:500],
        url_site=url_site.strip()[:500],
    )
