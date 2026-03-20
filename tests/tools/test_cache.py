import asyncio

import pytest

from tools.cache import cache_pagina, invalidar_cache


@pytest.mark.anyio
async def test_cache_pagina_retorna_resultado():
    chamadas = 0

    @cache_pagina("teste", ttl=60)
    async def funcao():
        nonlocal chamadas
        chamadas += 1
        return {"dado": "valor"}

    resultado = await funcao()
    assert resultado == {"dado": "valor"}
    assert chamadas == 1


@pytest.mark.anyio
async def test_cache_pagina_usa_cache_na_segunda_chamada():
    chamadas = 0

    @cache_pagina("teste_cache", ttl=60)
    async def funcao():
        nonlocal chamadas
        chamadas += 1
        return {"dado": "valor"}

    await funcao()
    await funcao()
    assert chamadas == 1


@pytest.mark.anyio
async def test_cache_pagina_com_argumentos_diferentes():
    chamadas = 0

    @cache_pagina("teste_args", ttl=60)
    async def funcao(pagina: int = 1):
        nonlocal chamadas
        chamadas += 1
        return {"pagina": pagina}

    await funcao(pagina=1)
    await funcao(pagina=2)
    assert chamadas == 2


@pytest.mark.anyio
async def test_invalidar_cache_limpa_tudo():
    chamadas = 0

    @cache_pagina("teste_invalidar", ttl=60)
    async def funcao():
        nonlocal chamadas
        chamadas += 1
        return {"dado": "valor"}

    await funcao()
    invalidar_cache()
    await funcao()
    assert chamadas == 2
