from bootstrap import app
from routes.api.busca import router as api_busca_router
from routes.api.feeds import router as api_feeds_router
from routes.api.status import router as api_status_router
from routes.web.admin import router as admin_router
from routes.web.feed import router as feed_router
from routes.web.feeds import router as feeds_router
from routes.web.home import router as home_router
from routes.web.seo import router as seo_router
from routes.web.sobre import router as sobre_router
from routes.web.sugestao import router as sugestao_router
from routes.web.tag import router as tag_router

app.include_router(home_router)
app.include_router(sobre_router)
app.include_router(sugestao_router)
app.include_router(admin_router)
app.include_router(tag_router)
app.include_router(feed_router)
app.include_router(feeds_router)
app.include_router(seo_router)
app.include_router(api_busca_router)
app.include_router(api_feeds_router)
app.include_router(api_status_router)
