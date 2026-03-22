import logging
import math

from tortoise import Tortoise
from unidecode import unidecode

from databases.models import Noticia

logger = logging.getLogger(__name__)

ITENS_POR_PAGINA = 20


def normalizar_termo(texto: str) -> str:
    return unidecode(texto).lower().strip()


async def criar_indice_fts() -> None:
    conn = Tortoise.get_connection("default")
    await conn.execute_script("""
        CREATE VIRTUAL TABLE IF NOT EXISTS noticia_fts USING fts5(
            noticia_id UNINDEXED,
            titulo,
            titulo_pt,
            resumo,
            tokenize='unicode61 remove_diacritics 2'
        );
    """)
    logger.info("Indice FTS5 criado/verificado")


async def reindexar_noticias() -> None:
    conn = Tortoise.get_connection("default")

    # Descobrir quais notícias já estão indexadas
    ja_indexadas = await conn.execute_query_dict(
        "SELECT noticia_id FROM noticia_fts"
    )
    ids_indexados = {r["noticia_id"] for r in ja_indexadas}

    # Buscar apenas notícias processadas que não estão no FTS
    noticias = await Noticia.filter(resumo_ia__not_isnull=True).values(
        "id", "titulo", "titulo_pt", "resumo_ia", "resumo_original"
    )
    novas = [n for n in noticias if n["id"] not in ids_indexados]

    if not novas:
        logger.info("FTS5 atualizado — nenhuma noticia nova para indexar")
        return

    # Remover do FTS notícias que não existem mais no banco
    ids_banco = {n["id"] for n in noticias}
    ids_remover = ids_indexados - ids_banco
    if ids_remover:
        placeholders = ",".join("?" * len(ids_remover))
        await conn.execute_query(
            f"DELETE FROM noticia_fts WHERE noticia_id IN ({placeholders})",
            list(ids_remover),
        )

    # Inserir novas em batch
    BATCH = 500
    for i in range(0, len(novas), BATCH):
        batch = novas[i : i + BATCH]
        valores = []
        for n in batch:
            valores.extend([
                n["id"],
                normalizar_termo(n["titulo"] or ""),
                normalizar_termo(n["titulo_pt"] or ""),
                normalizar_termo(n["resumo_ia"] or n["resumo_original"] or ""),
            ])
        placeholders = ",".join(["(?, ?, ?, ?)"] * len(batch))
        await conn.execute_query(
            f"INSERT INTO noticia_fts (noticia_id, titulo, titulo_pt, resumo) VALUES {placeholders}",
            valores,
        )

    logger.info("Reindexadas %d noticias novas no FTS5 (%d ja indexadas)", len(novas), len(ids_indexados))


async def indexar_noticia(noticia_id: int, titulo: str, titulo_pt: str | None, resumo: str) -> None:
    conn = Tortoise.get_connection("default")
    t = normalizar_termo(titulo)
    tp = normalizar_termo(titulo_pt or "")
    r = normalizar_termo(resumo)

    await conn.execute_query(
        "INSERT OR REPLACE INTO noticia_fts (noticia_id, titulo, titulo_pt, resumo) VALUES (?, ?, ?, ?)",
        [noticia_id, t, tp, r],
    )


async def buscar_noticias(termo: str, pagina: int = 1) -> dict:
    conn = Tortoise.get_connection("default")
    termo_normalizado = normalizar_termo(termo)

    if not termo_normalizado:
        return {"noticias": [], "pagina": 1, "total_paginas": 1, "termo": termo}

    # FTS5 match com wildcard pra busca parcial
    termo_fts = " ".join(f"{p}*" for p in termo_normalizado.split() if p)

    count_rows = await conn.execute_query_dict(
        "SELECT COUNT(*) as total FROM noticia_fts WHERE noticia_fts MATCH ?",
        [termo_fts],
    )
    total = count_rows[0]["total"] if count_rows else 0
    total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA

    rows = await conn.execute_query_dict(
        """
        SELECT noticia_id, rank
        FROM noticia_fts
        WHERE noticia_fts MATCH ?
        ORDER BY rank
        LIMIT ? OFFSET ?
        """,
        [termo_fts, ITENS_POR_PAGINA, offset],
    )

    ids = [r["noticia_id"] for r in rows]

    if not ids:
        return {"noticias": [], "pagina": pagina, "total_paginas": total_paginas, "termo": termo}

    noticias = await Noticia.filter(id__in=ids, resumo_ia__not_isnull=True).prefetch_related("feed", "tags")

    # manter a ordem do ranking FTS
    ordem = {nid: i for i, nid in enumerate(ids)}
    noticias_sorted = sorted(noticias, key=lambda n: ordem.get(n.id, 999))

    for noticia in noticias_sorted:
        noticia.tags_list = list(noticia.tags)

    return {
        "noticias": noticias_sorted,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "termo": termo,
    }
