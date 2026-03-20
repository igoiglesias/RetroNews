import pytest

from databases.models import Sugestao


@pytest.mark.anyio
async def test_formulario_sugestao(cliente):
    resposta = await cliente.get("/sugerir")
    assert resposta.status_code == 200
    assert "csrf_token" in resposta.text
    assert "nome_site" in resposta.text


@pytest.mark.anyio
async def test_enviar_sugestao_sem_csrf(cliente):
    resposta = await cliente.post("/sugerir", data={
        "nome_site": "Blog", "url_site": "https://blog.com",
        "csrf_token": "invalido", "honeypot": "",
    })
    assert resposta.status_code == 200
    assert "expirada" in resposta.text.lower() or "Tente novamente" in resposta.text


@pytest.mark.anyio
async def test_enviar_sugestao_honeypot(cliente):
    resposta = await cliente.post("/sugerir", data={
        "nome_site": "Blog", "url_site": "https://blog.com",
        "csrf_token": "x", "honeypot": "bot_value",
    }, follow_redirects=False)
    assert resposta.status_code == 303


@pytest.mark.anyio
async def test_enviar_sugestao_spam(cliente):
    # pega um csrf valido primeiro
    get_resp = await cliente.get("/sugerir")
    import re
    match = re.search(r'value="(\d+:[a-f0-9]+)"', get_resp.text)
    csrf = match.group(1) if match else "invalid"

    resposta = await cliente.post("/sugerir", data={
        "nome_site": "buy now free money",
        "url_site": "https://blog.com",
        "csrf_token": csrf,
        "honeypot": "",
    })
    assert resposta.status_code == 200
    assert "spam" in resposta.text.lower()
