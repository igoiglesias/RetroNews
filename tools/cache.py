import functools
import pickle
from typing import Any

from fastapi_cache import FastAPICache


def cache_pagina(chave: str, ttl: int = 300):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{chave}:{args}:{sorted(kwargs.items())}"
            try:
                backend = FastAPICache.get_backend()
            except Exception:
                return await func(*args, **kwargs)

            cached = await backend.get(cache_key)
            if cached is not None:
                return pickle.loads(cached)  # noqa: S301 - internal cache, trusted data only

            resultado = await func(*args, **kwargs)
            await backend.set(cache_key, pickle.dumps(resultado), ttl)
            return resultado
        return wrapper
    return decorator


async def invalidar_cache(*chaves: str):
    try:
        backend = FastAPICache.get_backend()
    except Exception:
        return

    if not chaves:
        if hasattr(backend, "_store"):
            backend._store.clear()
    else:
        for chave in chaves:
            await backend.clear(namespace=chave)
