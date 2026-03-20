import math

from databases.models import Feed, Sugestao

ITENS_POR_PAGINA = 20


async def criar_sugestao(nome_site: str, url_site: str, url_rss: str, motivo: str, ip: str) -> Sugestao:
    return await Sugestao.create(
        nome_site=nome_site.strip()[:200],
        url_site=url_site.strip()[:500],
        url_rss=url_rss.strip()[:500],
        motivo=motivo.strip()[:1000],
        ip_remetente=ip,
    )


async def listar_sugestoes(status: str = "pendente", pagina: int = 1) -> dict:
    query = Sugestao.filter(status=status)
    total = await query.count()
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    sugestoes = await query.order_by("-criado_em").offset(offset).limit(ITENS_POR_PAGINA)

    return {
        "sugestoes": sugestoes,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "status_filtro": status,
    }


async def aprovar_sugestao(sugestao_id: int) -> bool:
    sugestao = await Sugestao.get_or_none(id=sugestao_id)
    if not sugestao or sugestao.status != "pendente":
        return False

    sugestao.status = "aprovada"
    await sugestao.save()

    if sugestao.url_rss:
        existe = await Feed.exists(url_rss=sugestao.url_rss)
        if not existe:
            await Feed.create(
                nome=sugestao.nome_site,
                url_rss=sugestao.url_rss,
                url_site=sugestao.url_site,
            )

    return True


async def rejeitar_sugestao(sugestao_id: int) -> bool:
    sugestao = await Sugestao.get_or_none(id=sugestao_id)
    if not sugestao or sugestao.status != "pendente":
        return False

    sugestao.status = "rejeitada"
    await sugestao.save()
    return True


async def contar_pendentes() -> int:
    return await Sugestao.filter(status="pendente").count()
