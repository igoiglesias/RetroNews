import pytest

from databases.models import Feed, Noticia
from services.busca import buscar_noticias, criar_indice_fts, indexar_noticia, normalizar_termo, reindexar_noticias


def test_normalizar_termo():
    assert normalizar_termo("Açúcar") == "acucar"
    assert normalizar_termo("  HELLO  ") == "hello"
    assert normalizar_termo("café") == "cafe"


@pytest.mark.anyio
async def test_criar_indice_e_reindexar():
    await criar_indice_fts()

    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    await Noticia.create(
        feed=feed, titulo="Python async programming",
        titulo_pt="Programacao assincrona em Python",
        url="https://f.com/1", resumo_original="Artigo sobre async",
        resumo_ia="Comentario sobre Python",
    )

    await reindexar_noticias()
    resultado = await buscar_noticias("python")
    assert len(resultado["noticias"]) == 1


@pytest.mark.anyio
async def test_busca_com_acentos():
    await criar_indice_fts()

    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    n = await Noticia.create(
        feed=feed, titulo="Programação avançada",
        url="https://f.com/2", resumo_original="Artigo tecnico",
    )
    await indexar_noticia(n.id, n.titulo, None, n.resumo_original)

    resultado = await buscar_noticias("programacao")
    assert len(resultado["noticias"]) == 1


@pytest.mark.anyio
async def test_busca_termo_vazio():
    resultado = await buscar_noticias("")
    assert resultado["noticias"] == []


@pytest.mark.anyio
async def test_busca_sem_resultados():
    await criar_indice_fts()
    resultado = await buscar_noticias("xyznonexistent")
    assert resultado["noticias"] == []
    assert resultado["termo"] == "xyznonexistent"
