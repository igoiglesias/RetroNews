import pytest

from databases.models import Feed, Sugestao
from services.sugestao import (
    aprovar_sugestao,
    contar_pendentes,
    criar_sugestao,
    listar_sugestoes,
    rejeitar_sugestao,
)


@pytest.mark.anyio
async def test_criar_sugestao():
    s = await criar_sugestao("Blog Test", "https://blog.com", "https://blog.com/rss", "Legal", "1.2.3.4")
    assert s.nome_site == "Blog Test"
    assert s.status == "pendente"
    assert s.ip_remetente == "1.2.3.4"


@pytest.mark.anyio
async def test_listar_sugestoes_pendentes():
    await Sugestao.create(nome_site="A", url_site="https://a.com", status="pendente")
    await Sugestao.create(nome_site="B", url_site="https://b.com", status="aprovada")

    dados = await listar_sugestoes(status="pendente")
    assert len(dados["sugestoes"]) == 1
    assert dados["sugestoes"][0].nome_site == "A"


@pytest.mark.anyio
async def test_aprovar_sugestao_cria_feed():
    s = await Sugestao.create(
        nome_site="Blog", url_site="https://blog.com",
        url_rss="https://blog.com/rss", status="pendente",
    )
    resultado = await aprovar_sugestao(s.id)
    assert resultado is True

    await s.refresh_from_db()
    assert s.status == "aprovada"

    feed = await Feed.get_or_none(url_rss="https://blog.com/rss")
    assert feed is not None
    assert feed.nome == "Blog"


@pytest.mark.anyio
async def test_aprovar_sugestao_sem_rss():
    s = await Sugestao.create(
        nome_site="Blog", url_site="https://blog.com", status="pendente",
    )
    resultado = await aprovar_sugestao(s.id)
    assert resultado is True

    feeds = await Feed.all().count()
    assert feeds == 0


@pytest.mark.anyio
async def test_aprovar_sugestao_inexistente():
    assert await aprovar_sugestao(999) is False


@pytest.mark.anyio
async def test_rejeitar_sugestao():
    s = await Sugestao.create(
        nome_site="Spam", url_site="https://spam.com", status="pendente",
    )
    resultado = await rejeitar_sugestao(s.id)
    assert resultado is True

    await s.refresh_from_db()
    assert s.status == "rejeitada"


@pytest.mark.anyio
async def test_rejeitar_sugestao_ja_aprovada():
    s = await Sugestao.create(
        nome_site="OK", url_site="https://ok.com", status="aprovada",
    )
    assert await rejeitar_sugestao(s.id) is False


@pytest.mark.anyio
async def test_contar_pendentes():
    await Sugestao.create(nome_site="A", url_site="https://a.com", status="pendente")
    await Sugestao.create(nome_site="B", url_site="https://b.com", status="pendente")
    await Sugestao.create(nome_site="C", url_site="https://c.com", status="aprovada")

    assert await contar_pendentes() == 2
