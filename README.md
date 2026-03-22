# RetroNews

Agregador de noticias dev com comentarios de IA e interface retro CRT.

Consome feeds RSS automaticamente, gera comentarios com humor nerd via IA (OpenRouter/gpt-4o-mini), traduz titulos para portugues e classifica com tags — tudo apresentado numa interface estilo terminal fosforo verde dos anos 80.

## Stack

- **Backend**: FastAPI + Tortoise ORM + SQLite (WAL mode)
- **Frontend**: Jinja2 SSR + CSS puro (estetica CRT) + busca inline com debounce
- **IA**: OpenRouter API (modelo configuravel via admin) para comentarios e tags
- **Busca**: SQLite FTS5 com suporte a acentos/fonetica, integrada na home
- **Scheduler**: APScheduler (atualizacao automatica configuravel, retry automatico com limite)

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
- **Dashboard**: visualizar stats gerais, status do processamento de IA, creditos OpenRouter restantes (com alerta de creditos baixos)
- **Feeds**: gerenciar feeds (ativar, desativar, editar, excluir)
- **Processamento**: monitorar noticias pendentes/com erro/falhadas, reprocessar individualmente, visualizar log de eventos
- **Config IA**: editar o system prompt e modelo usados pela IA (salvo no banco, sem tocar no .env)
- **Sugestoes**: aprovar/rejeitar sugestoes de feeds dos usuarios
- **Senha**: trocar senha do admin

## Fluxo de Processamento

1. Scheduler busca novos artigos dos feeds RSS a cada N minutos
2. Noticias novas sao salvas no banco (sem resumo IA)
3. IA processa cada noticia: traduz titulo, gera comentario, classifica tags
4. Em caso de erro, registra a mensagem e incrementa contador de tentativas
5. Noticias com erro sao reprocessadas automaticamente no proximo ciclo (max 3 tentativas)
6. Apenas noticias processadas com sucesso aparecem para os usuarios
7. Noticias que falharam 3x ficam visiveis no admin para intervencao manual

## Comandos

| Comando | Descricao |
|---------|-----------|
| `make dev` | Servidor dev com hot reload (scheduler desativado) |
| `make prod` | Servidor producao (gunicorn + uvicorn worker) |
| `make test` | Rodar todos os testes |
| `make test-one path=tests/...` | Rodar teste especifico |
| `make cov` | Testes com relatorio de cobertura |
| `make script name=seed_feeds` | Popular banco com feeds + admin |
| `make reprocessar` | Reprocessar noticias com erro (dedup + retry) |

## Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `OPENROUTER_API_KEY` | _(vazio)_ | Chave da API OpenRouter (obrigatoria para IA) |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Modelo usado para comentarios (editavel no admin) |
| `APP_DEBUG` | `False` | Habilita /docs e endpoint de atualizacao manual |
| `JWT_SECRET` | _(padrao inseguro)_ | Secret para tokens JWT do admin |
| `SCHEDULER_INTERVALO_MINUTOS` | `60` | Intervalo de atualizacao dos feeds |
| `MAX_TENTATIVAS_IA` | `3` | Numero maximo de tentativas de processamento IA |
| `OPENROUTER_ALERTA_CREDITOS` | `1.0` | Valor em USD para alerta de creditos baixos |
| `RATE_LIMIT` | `30/minute` | Limite de requisicoes por IP |
| `COOKIE_DOMAIN` | _(vazio)_ | Dominio do cookie JWT |
| `COOKIE_SECURE` | `False` | Cookies HTTPS only |

## Estrutura

```
app.py              # Registra routers
bootstrap.py        # FastAPI init, lifespan, middlewares, filtros Jinja2
config/config.py    # Leitura unica de .env
databases/models.py # Feed, Noticia, Tag, Sugestao, Admin, ConfigIA, LogProcessamento
services/           # Logica de negocio (feed, resumo, busca, admin, config_ia, log)
modules/            # Clientes HTTP (OpenRouter)
tools/              # Utilitarios puros (cache, html, seguranca)
routes/web/         # Rotas SSR (Jinja2)
routes/api/         # Rotas JSON (status, busca)
templates/          # HTML (base, components, pages, partials)
static/             # CSS, JS, fontes
scripts/            # Seed e utilitarios
tests/              # Espelha a estrutura da app
```
