import pytest


@pytest.mark.anyio
async def test_sobre_retorna_200(cliente):
    resposta = await cliente.get("/sobre")
    assert resposta.status_code == 200


@pytest.mark.anyio
async def test_sobre_contem_html(cliente):
    resposta = await cliente.get("/sobre")
    assert "text/html" in resposta.headers["content-type"]


@pytest.mark.anyio
async def test_sobre_contem_descricao(cliente):
    resposta = await cliente.get("/sobre")
    assert "agregador" in resposta.text.lower()
