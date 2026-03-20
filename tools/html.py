import html
import logging
import re

import httpx

logger = logging.getLogger(__name__)


def limpar_html(texto: str) -> str:
    if not texto:
        return ""
    sem_tags = re.sub(r"<[^>]+>", "", texto)
    return html.unescape(sem_tags).strip()


def truncar(texto: str, limite: int) -> str:
    if not texto or len(texto) <= limite:
        return texto
    return texto[: limite - 3] + "..."


async def extrair_texto_pagina(url: str) -> str:
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resposta = await client.get(url, timeout=15.0, headers={
                "User-Agent": "RetroNews/1.0 (agregador de noticias)"
            })
            resposta.raise_for_status()

        corpo = resposta.text

        # remove script, style, nav, header, footer
        for tag in ["script", "style", "nav", "header", "footer", "aside"]:
            corpo = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", corpo, flags=re.DOTALL | re.IGNORECASE)

        # tenta extrair <article> ou <main> primeiro
        for container in ["article", "main"]:
            match = re.search(rf"<{container}[^>]*>(.*?)</{container}>", corpo, flags=re.DOTALL | re.IGNORECASE)
            if match:
                corpo = match.group(1)
                break

        texto = limpar_html(corpo)
        # colapsa whitespace excessivo
        texto = re.sub(r"\s+", " ", texto).strip()

        if len(texto) < 50:
            return ""

        return texto[:3000]

    except Exception as e:
        logger.warning("Erro ao extrair texto de %s: %s", url, e)
        return ""
