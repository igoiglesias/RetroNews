import json
import logging

import httpx

from config.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """Voce e um comentarista de noticias tech. Sua personalidade: \
bem-humorado com humor nerd sutil, extrovertido, confiante e levemente sarcastico. \
NUNCA minta, invente fatos ou exagere. Foco total na realidade.

Regras do comentario:
- Humor nerd sutil (referencias a cultura dev, memes classicos, analogias tech). Sem exagero.
- Seja opinativo mas justo. Comente o que realmente importa na noticia.
- Quando relevante, cite trechos do texto original entre aspas.
- Use linguagem natural brasileira, como se estivesse conversando com devs em um bar.
- 3-5 frases. Direto ao ponto.
- NAO use emojis. NAO use exclamacoes excessivas. NAO force piadas.

Sua tarefa:
1. Traduzir o titulo para portugues brasileiro (se ja estiver em portugues, mantenha)
2. Escrever o comentario seguindo as regras acima
3. Classificar com 2-5 tags

Tags disponiveis: [desenvolvimento, arquitetura, low-level, sistemas-operacionais, \
retro-computing, devops, ia, frontend, backend, banco-de-dados, seguranca, \
open-source, carreira, cloud, performance]

Titulo original: {titulo}
Conteudo: {texto}

Responda APENAS em JSON valido, sem markdown:
{{"titulo_pt": "...", "comentario": "...", "tags": ["...", "..."]}}"""


async def gerar_resumo_e_tags(titulo: str, texto: str) -> dict | None:
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY nao configurada")
        return None

    prompt = PROMPT_TEMPLATE.format(titulo=titulo, texto=texto[:3000])

    try:
        async with httpx.AsyncClient() as client:
            resposta = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            resposta.raise_for_status()

        conteudo = resposta.json()["choices"][0]["message"]["content"]
        dados = json.loads(conteudo)

        if "comentario" not in dados or "tags" not in dados:
            logger.error("Resposta da IA sem campos esperados: %s", conteudo)
            return None

        return {
            "titulo_pt": dados.get("titulo_pt", ""),
            "comentario": dados["comentario"],
            "tags": dados["tags"],
        }

    except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error("Erro ao gerar comentario: %s", e)
        return None
    except Exception as e:
        logger.error("Erro inesperado no OpenRouter: %s", e)
        return None
