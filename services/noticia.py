import math

from databases.models import Feed, Noticia, Tag
from tools.cache import cache_pagina

ITENS_POR_PAGINA = 20


@cache_pagina("noticias", ttl=300)
async def listar_noticias(pagina: int = 1) -> dict:
    total = await Noticia.all().count()
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    noticias = (
        await Noticia.all()
        .prefetch_related("feed", "tags")
        .order_by("-data_publicacao", "-criado_em")
        .offset(offset)
        .limit(ITENS_POR_PAGINA)
    )

    for noticia in noticias:
        noticia.tags_list = list(noticia.tags)

    return {
        "noticias": noticias,
        "pagina": pagina,
        "total_paginas": total_paginas,
    }


@cache_pagina("tag", ttl=300)
async def listar_por_tag(nome: str, pagina: int = 1) -> dict:
    tag_obj = await Tag.get_or_none(nome=nome)

    if not tag_obj:
        return {"noticias": [], "pagina": 1, "total_paginas": 1, "nome_tag": nome}

    total = await tag_obj.noticias.all().count()
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    noticias = (
        await tag_obj.noticias.all()
        .prefetch_related("feed", "tags")
        .order_by("-data_publicacao", "-criado_em")
        .offset(offset)
        .limit(ITENS_POR_PAGINA)
    )

    for noticia in noticias:
        noticia.tags_list = list(noticia.tags)

    return {
        "noticias": noticias,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "nome_tag": nome,
    }


@cache_pagina("feed", ttl=300)
async def listar_por_feed(feed_id: int, pagina: int = 1) -> dict | None:
    feed_obj = await Feed.get_or_none(id=feed_id)
    if not feed_obj:
        return None

    total = await Noticia.filter(feed=feed_obj).count()
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    noticias = (
        await Noticia.filter(feed=feed_obj)
        .prefetch_related("feed", "tags")
        .order_by("-data_publicacao", "-criado_em")
        .offset(offset)
        .limit(ITENS_POR_PAGINA)
    )

    for noticia in noticias:
        noticia.tags_list = list(noticia.tags)

    return {
        "noticias": noticias,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "nome_feed": feed_obj.nome,
        "feed_id": feed_id,
    }


@cache_pagina("feeds_lista", ttl=300)
async def listar_feeds() -> dict:
    feeds = await Feed.all().order_by("nome")
    return {"feeds": feeds}


async def obter_status() -> dict:
    total_feeds = await Feed.filter(ativo=True).count()
    total_noticias = await Noticia.all().count()
    ultima = await Noticia.all().order_by("-criado_em").first()
    ultima_atualizacao = ultima.criado_em.isoformat() if ultima else None

    return {
        "total_feeds": total_feeds,
        "total_noticias": total_noticias,
        "ultima_atualizacao": ultima_atualizacao,
    }
