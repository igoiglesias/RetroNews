# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

RetroNews — agregador de notícias dev com comentários de IA e UI retro CRT. FastAPI + Tortoise ORM + SQLite + Jinja2 SSR.

## Commands

```bash
make install          # Cria venv e instala dependências
make dev              # Servidor dev com hot reload (porta 8000)
make test             # Roda todos os testes
make test-one path=tests/services/test_feed.py  # Roda teste específico
make cov              # Testes com relatório de cobertura
make script name=seed_feeds   # Popula banco com feeds + admin padrão (admin/admin123)
```

Sempre usar Makefile — nunca chamar python ou pytest diretamente.

## Architecture

```
routes/ (thin HTTP handlers)  →  services/ (business logic)  →  databases/models.py (Tortoise ORM)
                                     ↓                              ↑
                                 modules/ (APIs externas)       tools/ (funções puras)
```

- **app.py**: registra routers. **bootstrap.py**: cria FastAPI, lifespan (Tortoise init, scheduler, FTS5), middlewares (GZip, security headers, rate limit).
- **config/config.py**: ponto único de leitura de `.env`. Nenhum outro arquivo usa `os.getenv`.
- Rotas são **finas** — delegam para services, nunca importam models diretamente.
- Services retornam dicts compatíveis com templates (ex: `{"noticias": [...], "pagina": 1, "total_paginas": 5}`).
- Toda a stack é **async**. Sem código sync em rotas, services ou modules.

## Key Flows

**Feed update**: `scheduler.py` (APScheduler, 30min) → `feed.py` (feedparser + scraping fallback) → `resumo.py` (OpenRouter AI gera comentário PT + tags) → `busca.py` (indexa no FTS5) → `cache.py` (invalida).

**Search**: SQLite FTS5 com `unicode61 remove_diacritics 2` + `unidecode` para normalização. Busca "programacao" encontra "Programação".

**Admin auth**: Login user/senha → bcrypt verify → JWT no cookie (httponly, samesite=strict, 8h) → cada rota valida JWT + verifica `sub` no banco.

## Conventions

- **Português em tudo**: variáveis, funções, tabelas, commits, logs (`buscar_por_email`, `criado_em`, `pagina`).
- **Paginação**: `?pagina=1` (1-indexed), `ITENS_POR_PAGINA = 20`, retorna `pagina` + `total_paginas`.
- **Cache**: decorator `@cache_pagina("chave", ttl=300)` em services. `invalidar_cache()` limpa tudo.
- **Deduplicação**: `Noticia.url` é unique — feed processing pula URLs existentes.
- **Segurança**: CSRF (HMAC-SHA256, 1h TTL), honeypot anti-bot, spam detection, rate limit (slowapi), security headers via middleware.

## Testing

- Testes usam `tmp_path` (tmpfs/RAM) — **nunca tocam o banco principal** em `databases/db.sqlite3`.
- Scheduler desabilitado nos testes via `RETRONEWS_DISABLE_SCHEDULER=1`.
- Fixture `cliente` fornece `httpx.AsyncClient` com `ASGITransport`.
- External calls (OpenRouter, feedparser, httpx) são mockados com `unittest.mock.patch`.
- **Coverage 100%** obrigatório em modules/, services/, routes/, tools/.
- Padrão: `@pytest.mark.anyio` + `async def test_nome_descritivo(cliente):`.

## Models (databases/models.py)

`Feed` (fontes RSS) → `Noticia` (artigos, FK Feed, M2M Tag, campos `titulo_pt` e `resumo_ia` preenchidos por IA) → `Tag` (geradas por IA) → `Sugestao` (sugestões de usuários, status pendente/aprovada/rejeitada) → `Admin` (usuario + senha_hash bcrypt).

Sem migrations — usa `generate_schemas=True`. Ao adicionar campo, deletar o `.sqlite3` e re-seed.
