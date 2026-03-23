from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from config.config import SITE_URL
from databases.models import Feed, Tag

router = APIRouter()


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


@router.get("/sitemap.xml")
async def sitemap_xml():
    urls = [
        (f"{SITE_URL}/", "1.0", "daily"),
        (f"{SITE_URL}/feeds", "0.7", "daily"),
        (f"{SITE_URL}/sobre", "0.3", "monthly"),
        (f"{SITE_URL}/sugerir", "0.3", "monthly"),
    ]

    feeds = await Feed.filter(ativo=True).all()
    for feed in feeds:
        urls.append((f"{SITE_URL}/feed/{feed.id}", "0.6", "daily"))

    tags = await Tag.all()
    for tag in tags:
        urls.append((f"{SITE_URL}/tag/{tag.nome}", "0.5", "daily"))

    xml_entries = []
    for loc, priority, changefreq in urls:
        xml_entries.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(xml_entries)
        + "\n</urlset>"
    )

    return Response(content=xml, media_type="application/xml")
