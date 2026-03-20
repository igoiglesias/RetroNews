import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.openrouter import gerar_resumo_e_tags


@pytest.mark.anyio
async def test_gerar_resumo_e_tags_sucesso():
    resposta_mock = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "titulo_pt": "Titulo em portugues",
                            "comentario": "Comentario sarcastico aqui.",
                            "tags": ["backend", "arquitetura"],
                        }
                    )
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = resposta_mock
    mock_response.raise_for_status = MagicMock()

    with patch("modules.openrouter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch("modules.openrouter.OPENROUTER_API_KEY", "test-key"):
            resultado = await gerar_resumo_e_tags("Title", "Article content")

    assert resultado is not None
    assert resultado["titulo_pt"] == "Titulo em portugues"
    assert resultado["comentario"] == "Comentario sarcastico aqui."
    assert resultado["tags"] == ["backend", "arquitetura"]


@pytest.mark.anyio
async def test_gerar_resumo_e_tags_erro_rede():
    with patch("modules.openrouter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Connection error")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch("modules.openrouter.OPENROUTER_API_KEY", "test-key"):
            resultado = await gerar_resumo_e_tags("Titulo", "Conteudo")

    assert resultado is None


@pytest.mark.anyio
async def test_gerar_resumo_e_tags_json_invalido():
    resposta_mock = {
        "choices": [
            {
                "message": {
                    "content": "isso nao e json"
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = resposta_mock
    mock_response.raise_for_status = MagicMock()

    with patch("modules.openrouter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch("modules.openrouter.OPENROUTER_API_KEY", "test-key"):
            resultado = await gerar_resumo_e_tags("Titulo", "Conteudo")

    assert resultado is None


@pytest.mark.anyio
async def test_gerar_resumo_e_tags_api_key_vazia():
    with patch("modules.openrouter.OPENROUTER_API_KEY", ""):
        resultado = await gerar_resumo_e_tags("Titulo", "Conteudo")
    assert resultado is None
