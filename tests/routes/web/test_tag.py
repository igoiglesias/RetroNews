import pytest

from databases.models import Feed, Noticia, Tag


@pytest.mark.anyio
async def test_tag_retorna_200(cliente):
    await Tag.create(nome="backend")
    resposta = await cliente.get("/tag/backend")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_tag_mostra_noticias_filtradas(cliente):
    feed = await Feed.create(nome="F", url_rss="https://f.com/rss", url_site="https://f.com")
    tag = await Tag.create(nome="devops")
    noticia = await Noticia.create(
        feed=feed, titulo="N DevOps", url="https://f.com/1",
        resumo_original="R", resumo_ia="Comentario IA",
    )
    await noticia.tags.add(tag)

    resposta = await cliente.get("/tag/devops")
    assert "N DevOps" in resposta.text


@pytest.mark.anyio
async def test_tag_inexistente(cliente):
    resposta = await cliente.get("/tag/inexistente")
    assert resposta.status_code == 200
    assert "Nenhuma noticia" in resposta.text
