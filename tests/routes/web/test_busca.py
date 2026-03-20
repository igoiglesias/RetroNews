import pytest

from databases.models import Feed, Noticia
from services.busca import criar_indice_fts, indexar_noticia


@pytest.mark.anyio
async def test_busca_pagina_sem_termo(cliente):
    await criar_indice_fts()
    resposta = await cliente.get("/busca")
    assert resposta.status_code == 200
    assert "buscar noticias" in resposta.text


@pytest.mark.anyio
async def test_busca_com_resultado(cliente):
    await criar_indice_fts()
    feed = await Feed.create(nome="Feed", url_rss="https://f.com/rss", url_site="https://f.com")
    n = await Noticia.create(
        feed=feed, titulo="Kubernetes scaling",
        url="https://f.com/k8s", resumo_original="K8s article",
    )
    await indexar_noticia(n.id, n.titulo, None, n.resumo_original)

    resposta = await cliente.get("/busca?q=kubernetes")
    assert resposta.status_code == 200
    assert "Kubernetes" in resposta.text


@pytest.mark.anyio
async def test_busca_sem_resultado(cliente):
    await criar_indice_fts()
    resposta = await cliente.get("/busca?q=xyznonexistent")
    assert resposta.status_code == 200
    assert "Nenhum resultado" in resposta.text
