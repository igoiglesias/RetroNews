import logging

from databases.models import ConfigIA
from config.config import OPENROUTER_MODEL
from modules.openrouter import PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

_cache_config: dict[str, str] = {}


async def inicializar_config_ia() -> None:
    existente = await ConfigIA.exists(chave="system_prompt")
    if not existente:
        await ConfigIA.create(chave="system_prompt", valor=PROMPT_TEMPLATE)
        await ConfigIA.create(chave="modelo", valor=OPENROUTER_MODEL)
        logger.info("ConfigIA inicializada com valores padrao")


async def obter_config_ia(chave: str) -> str | None:
    if chave in _cache_config:
        return _cache_config[chave]

    config = await ConfigIA.get_or_none(chave=chave)
    if config:
        _cache_config[chave] = config.valor
        return config.valor
    return None


async def salvar_config_ia(chave: str, valor: str) -> None:
    config, _ = await ConfigIA.get_or_create(chave=chave, defaults={"valor": valor})
    if config.valor != valor:
        config.valor = valor
        await config.save()
    _cache_config[chave] = valor


def invalidar_cache_config() -> None:
    _cache_config.clear()
