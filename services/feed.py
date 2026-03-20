import logging
from datetime import datetime
from time import mktime

import feedparser

from databases.models import Feed, Noticia
from services.resumo import processar_noticias_pendentes
from tools.cache import invalidar_cache
from tools.html import extrair_texto_pagina, limpar_html

logger = logging.getLogger(__name__)


async def buscar_todos_feeds() -> list[Feed]:
    return await Feed.filter(ativo=True).all()


async def processar_feed(feed: Feed) -> None:
    try:
        resultado = feedparser.parse(feed.url_rss)
    except Exception as e:
        logger.error("Erro ao buscar feed %s: %s", feed.nome, e)
        return

    if resultado.bozo and not resultado.entries:
        logger.warning("Feed %s retornou XML invalido", feed.nome)
        return

    for entrada in resultado.entries:
        titulo = entrada.get("title")
        url = entrada.get("link")

        if not titulo or not url:
            continue

        existe = await Noticia.exists(url=url)
        if existe:
            continue

        try:
            resumo_original = limpar_html(entrada.get("summary", ""))
            if not resumo_original or len(resumo_original) < 50:
                texto_pagina = await extrair_texto_pagina(url)
                if texto_pagina:
                    resumo_original = texto_pagina
            autor = entrada.get("author")
            if autor and len(autor) > 200:
                autor = autor[:197] + "..."
            data_publicacao = None

            parsed_date = entrada.get("published_parsed")
            if parsed_date:
                try:
                    data_publicacao = datetime.fromtimestamp(mktime(parsed_date))
                except (ValueError, OverflowError):
                    pass

            await Noticia.create(
                feed=feed,
                titulo=titulo[:500],
                url=url,
                resumo_original=resumo_original,
                autor=autor,
                data_publicacao=data_publicacao,
            )
            logger.info("Nova noticia: %s", titulo)
        except Exception as e:
            logger.error("Erro ao salvar noticia '%s': %s", titulo, e)


async def atualizar_todos_feeds() -> None:
    feeds = await buscar_todos_feeds()
    logger.info("Atualizando %d feeds", len(feeds))

    for feed in feeds:
        await processar_feed(feed)

    await processar_noticias_pendentes()
    invalidar_cache()
    logger.info("Atualizacao concluida")
