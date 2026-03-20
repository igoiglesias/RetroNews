import logging

from databases.models import Noticia, Tag
from modules.openrouter import gerar_resumo_e_tags
from services.busca import indexar_noticia

logger = logging.getLogger(__name__)


async def gerar_resumo(noticia: Noticia) -> None:
    resultado = await gerar_resumo_e_tags(noticia.titulo, noticia.resumo_original)

    if resultado is None:
        logger.warning("Nao foi possivel gerar comentario para: %s", noticia.titulo)
        return

    noticia.resumo_ia = resultado["comentario"]
    if resultado["titulo_pt"]:
        noticia.titulo_pt = resultado["titulo_pt"]
    await noticia.save()

    for nome_tag in resultado["tags"]:
        tag, _ = await Tag.get_or_create(nome=nome_tag.lower().strip())
        await noticia.tags.add(tag)

    try:
        await indexar_noticia(
            noticia.id, noticia.titulo, noticia.titulo_pt,
            noticia.resumo_ia or noticia.resumo_original,
        )
    except Exception as e:
        logger.warning("Erro ao indexar noticia %d: %s", noticia.id, e)

    logger.info("Comentario gerado para: %s", noticia.titulo)


async def processar_noticias_pendentes() -> None:
    pendentes = await Noticia.filter(resumo_ia=None).all()
    logger.info("Noticias pendentes de comentario: %d", len(pendentes))

    for noticia in pendentes:
        await gerar_resumo(noticia)
