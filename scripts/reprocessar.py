import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise

from config.config import DB_PATH, MAX_TENTATIVAS_IA


async def main():
    await Tortoise.init(
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["databases.models"]},
    )

    from databases.models import Noticia

    # 1. Remover noticias duplicadas por URL (manter a mais antiga)
    conn = Tortoise.get_connection("default")
    duplicadas = await conn.execute_query_dict(
        "SELECT url, COUNT(*) as total FROM noticia GROUP BY url HAVING total > 1"
    )

    total_removidas = 0
    for dup in duplicadas:
        noticias = await Noticia.filter(url=dup["url"]).order_by("criado_em")
        for noticia in noticias[1:]:
            await noticia.delete()
            total_removidas += 1

    if total_removidas:
        print(f"Removidas {total_removidas} noticias duplicadas.")

    # 2. Resetar tentativas de noticias com erro para reprocessamento
    com_erro = await Noticia.filter(
        resumo_ia__isnull=True,
        tentativas_ia__gte=MAX_TENTATIVAS_IA,
    ).count()

    if com_erro:
        await Noticia.filter(
            resumo_ia__isnull=True,
            tentativas_ia__gte=MAX_TENTATIVAS_IA,
        ).update(tentativas_ia=0, erro_ia=None)
        print(f"Resetadas {com_erro} noticias com erro para reprocessamento.")
    else:
        print("Nenhuma noticia com erro para reprocessar.")

    # 3. Mostrar resumo
    pendentes = await Noticia.filter(
        resumo_ia__isnull=True,
        tentativas_ia__lt=MAX_TENTATIVAS_IA,
    ).count()
    processadas = await Noticia.filter(resumo_ia__not_isnull=True).count()
    print(f"\nResumo: {processadas} processadas, {pendentes} pendentes de IA.")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
