from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tools.html import extrair_texto_pagina, limpar_html, truncar


def test_limpar_html_remove_tags():
    assert limpar_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_limpar_html_texto_sem_tags():
    assert limpar_html("texto puro") == "texto puro"


def test_limpar_html_texto_vazio():
    assert limpar_html("") == ""


def test_limpar_html_converte_entidades():
    assert limpar_html("&amp; &lt; &gt;") == "& < >"


def test_truncar_texto_curto():
    assert truncar("abc", 10) == "abc"


def test_truncar_texto_longo():
    resultado = truncar("abcdefghij", 5)
    assert resultado == "ab..."
    assert len(resultado) <= 5


def test_truncar_texto_exato():
    assert truncar("abcde", 5) == "abcde"


def test_truncar_texto_vazio():
    assert truncar("", 10) == ""


@pytest.mark.anyio
async def test_extrair_texto_pagina_com_article():
    html_fake = """
    <html><body>
    <nav>menu</nav>
    <article><p>Conteudo do artigo que e suficientemente longo para passar o limite minimo de cinquenta caracteres.</p></article>
    <footer>rodape</footer>
    </body></html>
    """
    mock_response = MagicMock()
    mock_response.text = html_fake
    mock_response.raise_for_status = MagicMock()

    with patch("tools.html.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        resultado = await extrair_texto_pagina("https://exemplo.com/artigo")

    assert "Conteudo do artigo" in resultado
    assert "menu" not in resultado
    assert "rodape" not in resultado


@pytest.mark.anyio
async def test_extrair_texto_pagina_erro_rede():
    with patch("tools.html.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Timeout")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        resultado = await extrair_texto_pagina("https://exemplo.com/falha")

    assert resultado == ""


@pytest.mark.anyio
async def test_extrair_texto_pagina_conteudo_curto():
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>Curto</p></body></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("tools.html.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        resultado = await extrair_texto_pagina("https://exemplo.com/curto")

    assert resultado == ""
