import functools
from typing import Any

from cachetools import TTLCache

_caches: list[TTLCache] = []


def cache_pagina(chave: str, ttl: int = 300):
    cache: TTLCache[str, Any] = TTLCache(maxsize=128, ttl=ttl)
    _caches.append(cache)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{chave}:{args}:{sorted(kwargs.items())}"
            if cache_key in cache:
                return cache[cache_key]
            resultado = await func(*args, **kwargs)
            cache[cache_key] = resultado
            return resultado
        return wrapper
    return decorator


def invalidar_cache():
    for cache in _caches:
        cache.clear()
