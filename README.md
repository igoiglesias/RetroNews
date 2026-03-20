# RetroNews

Agregador de noticias dev com comentarios de IA e interface retro CRT.

Consome feeds RSS automaticamente, gera comentarios com humor nerd via IA (OpenRouter/gpt-4o-mini), traduz titulos para portugues e classifica com tags — tudo apresentado numa interface estilo terminal fosforo verde dos anos 80.

## Stack

- **Backend**: FastAPI + Tortoise ORM + SQLite
- **Frontend**: Jinja2 SSR + CSS puro (estetica CRT)
- **IA**: OpenRouter API (gpt-4o-mini) para comentarios e tags
- **Busca**: SQLite FTS5 com suporte a acentos/fonetica
- **Scheduler**: APScheduler (atualizacao automatica a cada 30min)

## Setup

```bash
# Instalar dependencias
make install

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com sua OPENROUTER_API_KEY

# Popular banco com feeds iniciais + admin
make script name=seed_feeds

# Iniciar servidor dev
make dev
```

Acesse `http://localhost:8000`

## Admin

Login em `/admin/login` com as credenciais criadas pelo seed (padrao: `admin` / `admin123`).

No painel admin voce pode:
- Gerenciar feeds (ativar, desativar, editar, excluir)
- Aprovar/rejeitar sugestoes de feeds dos usuarios
- Forcar atualizacao de feeds
- Trocar senha

## Comandos

| Comando | Descricao |
|---------|-----------|
| `make dev` | Servidor dev com hot reload |
| `make test` | Rodar todos os testes |
| `make test-one path=tests/...` | Rodar teste especifico |
| `make cov` | Testes com relatorio de cobertura |
| `make script name=seed_feeds` | Popular banco com feeds + admin |
| `make prod` | Servidor producao (uvicorn) |

## Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `OPENROUTER_API_KEY` | _(vazio)_ | Chave da API OpenRouter (obrigatoria para IA) |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Modelo usado para comentarios |
| `APP_DEBUG` | `False` | Habilita /docs e endpoint de atualizacao manual |
| `JWT_SECRET` | _(padrao inseguro)_ | Secret para tokens JWT do admin |
| `SCHEDULER_INTERVALO_MINUTOS` | `30` | Intervalo de atualizacao dos feeds |
| `RATE_LIMIT` | `30/minute` | Limite de requisicoes por IP |

## Estrutura

```
app.py              # Registra routers
bootstrap.py        # FastAPI init, lifespan, middlewares
config/config.py    # Leitura unica de .env
databases/models.py # Feed, Noticia, Tag, Sugestao, Admin
services/           # Logica de negocio (feed, resumo, busca, admin)
modules/            # Clientes HTTP (OpenRouter)
tools/              # Utilitarios puros (cache, html, seguranca)
routes/web/         # Rotas SSR (Jinja2)
routes/api/         # Rotas JSON
templates/          # HTML (base, components, pages)
static/             # CSS, JS, fontes
scripts/            # Seed e utilitarios
tests/              # Espelha a estrutura da app
```
