from unittest.mock import AsyncMock, patch

import pytest

from databases.models import Feed, Noticia, Tag
from services.resumo import gerar_resumo, processar_noticias_pendentes


@pytest.mark.anyio
async def test_gerar_resumo_salva_comentario_e_tags():
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    noticia = await Noticia.create(
        feed=feed, titulo="Original Title", url="https://f.com/1", resumo_original="Original"
    )

    mock_resultado = {
        "titulo_pt": "Titulo Traduzido",
        "comentario": "Comentario sarcastico.",
        "tags": ["backend", "devops"],
    }

    with patch("services.resumo.gerar_resumo_e_tags", new_callable=AsyncMock, return_value=mock_resultado):
        await gerar_resumo(noticia)

    await noticia.refresh_from_db()
    assert noticia.resumo_ia == "Comentario sarcastico."
    assert noticia.titulo_pt == "Titulo Traduzido"

    tags = await noticia.tags.all()
    nomes = [t.nome for t in tags]
    assert "backend" in nomes
    assert "devops" in nomes


@pytest.mark.anyio
async def test_gerar_resumo_ia_retorna_none():
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    noticia = await Noticia.create(
        feed=feed, titulo="Titulo", url="https://f.com/2", resumo_original="Original"
    )

    with patch("services.resumo.gerar_resumo_e_tags", new_callable=AsyncMock, return_value=None):
        await gerar_resumo(noticia)

    await noticia.refresh_from_db()
    assert noticia.resumo_ia is None
    assert noticia.titulo_pt is None


@pytest.mark.anyio
async def test_gerar_resumo_sem_titulo_pt():
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    noticia = await Noticia.create(
        feed=feed, titulo="Titulo PT", url="https://f.com/6", resumo_original="Original"
    )

    mock_resultado = {"titulo_pt": "", "comentario": "Comentario.", "tags": ["ia"]}

    with patch("services.resumo.gerar_resumo_e_tags", new_callable=AsyncMock, return_value=mock_resultado):
        await gerar_resumo(noticia)

    await noticia.refresh_from_db()
    assert noticia.titulo_pt is None
    assert noticia.resumo_ia == "Comentario."


@pytest.mark.anyio
async def test_gerar_resumo_reutiliza_tags_existentes():
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    await Tag.create(nome="backend")
    noticia = await Noticia.create(
        feed=feed, titulo="Titulo", url="https://f.com/3", resumo_original="Original"
    )

    mock_resultado = {"titulo_pt": "Titulo", "comentario": "Comentario.", "tags": ["backend"]}

    with patch("services.resumo.gerar_resumo_e_tags", new_callable=AsyncMock, return_value=mock_resultado):
        await gerar_resumo(noticia)

    assert await Tag.filter(nome="backend").count() == 1


@pytest.mark.anyio
async def test_processar_noticias_pendentes():
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(feed=feed, titulo="Pendente", url="https://f.com/4", resumo_original="Orig")
    await Noticia.create(
        feed=feed, titulo="Ja tem", url="https://f.com/5", resumo_original="Orig", resumo_ia="Pronto"
    )

    with patch("services.resumo.gerar_resumo") as mock_gerar:
        mock_gerar.return_value = None
        await processar_noticias_pendentes()

    mock_gerar.assert_called_once()
