import pytest

from databases.models import Feed, Noticia
from services.busca import criar_indice_fts, indexar_noticia


@pytest.mark.anyio
async def test_busca_na_home_sem_termo(cliente):
    resposta = await cliente.get("/")
    assert resposta.status_code == 200
    assert "buscar noticias" in resposta.text


@pytest.mark.anyio
async def test_busca_na_home_com_resultado(cliente):
    await criar_indice_fts()
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    n = await Noticia.create(
        feed=feed, titulo="Kubernetes scaling",
        url="https://f.com/k8s", resumo_original="K8s article",
        resumo_ia="Comentario sobre K8s",
    )
    await indexar_noticia(n.id, n.titulo, None, n.resumo_ia)

    resposta = await cliente.get("/?q=kubernetes")
    assert resposta.status_code == 200
    assert "Kubernetes" in resposta.text


@pytest.mark.anyio
async def test_busca_na_home_sem_resultado(cliente):
    await criar_indice_fts()
    resposta = await cliente.get("/?q=xyznonexistent")
    assert resposta.status_code == 200
    assert "Nenhum resultado" in resposta.text


@pytest.mark.anyio
async def test_api_busca_retorna_html(cliente):
    await criar_indice_fts()
    feed = await Feed.create(nome="Feed", url_rss="https://fb.com/rss", url_site="https://fb.com")
    n = await Noticia.create(
        feed=feed, titulo="Docker containers",
        url="https://fb.com/docker", resumo_original="Docker article",
        resumo_ia="Comentario sobre Docker",
    )
    await indexar_noticia(n.id, n.titulo, None, n.resumo_ia)

    resposta = await cliente.get("/api/busca?q=docker")
    assert resposta.status_code == 200
    assert "Docker" in resposta.text
