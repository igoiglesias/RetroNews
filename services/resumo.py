import logging

from config.config import MAX_TENTATIVAS_IA
from databases.models import LogProcessamento, Noticia, Tag
from modules.openrouter import gerar_resumo_e_tags
from services.busca import indexar_noticia

logger = logging.getLogger(__name__)


async def registrar_log(tipo: str, mensagem: str, detalhes: str | None = None) -> None:
    await LogProcessamento.create(tipo=tipo, mensagem=mensagem, detalhes=detalhes)


async def gerar_resumo(noticia: Noticia) -> None:
    noticia.tentativas_ia += 1

    from services.config_ia import obter_config_ia
    prompt_template = await obter_config_ia("system_prompt")
    modelo = await obter_config_ia("modelo")

    try:
        resultado = await gerar_resumo_e_tags(
            noticia.titulo, noticia.resumo_original,
            prompt_template=prompt_template, modelo=modelo,
        )
    except Exception as e:
        noticia.erro_ia = str(e)
        await noticia.save()
        await registrar_log("ia_erro", f"Erro ao chamar IA para: {noticia.titulo}", str(e))
        logger.error("Erro na chamada IA para noticia %d: %s", noticia.id, e)
        return

    if resultado is None:
        noticia.erro_ia = "IA retornou resposta vazia ou invalida"
        await noticia.save()
        await registrar_log("ia_erro", f"IA sem resposta para: {noticia.titulo}")
        logger.warning("Nao foi possivel gerar comentario para: %s", noticia.titulo)
        return

    noticia.resumo_ia = resultado["comentario"]
    noticia.erro_ia = None
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

    await registrar_log("ia_sucesso", f"Comentario gerado para: {noticia.titulo}")
    logger.info("Comentario gerado para: %s", noticia.titulo)


async def processar_noticias_pendentes() -> None:
    pendentes = await Noticia.filter(
        resumo_ia__isnull=True,
        tentativas_ia__lt=MAX_TENTATIVAS_IA,
    ).all()
    logger.info("Noticias pendentes de comentario: %d", len(pendentes))

    for noticia in pendentes:
        try:
            await gerar_resumo(noticia)
        except Exception as e:
            logger.error("Erro ao gerar resumo para noticia %d: %s", noticia.id, e)
