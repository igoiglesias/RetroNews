import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise

from config.config import DB_PATH
from databases.models import Admin, Feed
from tools.seguranca import hash_senha

FEEDS = [
    # --- Multi-linguagem / Comparativo ---
    ("Verdagon (Vale lang + memory safety)", "https://verdagon.dev/rss.xml", "https://verdagon.dev"),
    # ^ Criador da linguagem Vale. Posts épicos comparando modelos de memória entre linguagens.
    ("Xe Iaso", "https://xeiaso.net/blog.rss", "https://xeiaso.net/blog"),
    # ^ Escreve sobre Nix, Zig, Rust, Go, Hare, Elixir. Prolífico e técnico.
    # --- Go (complemento pra tua trilha) ---
    ("Go Blog (oficial)", "https://go.dev/blog/feed.atom", "https://go.dev/blog"),
    # --- Rust (complemento) ---
    ("This Week in Rust", "https://this-week-in-rust.org/rss.xml", "https://this-week-in-rust.org"),
    # ^ Newsletter semanal do ecossistema Rust. Excelente curadoria.
    ("Rust Blog (oficial)", "https://blog.rust-lang.org/feed.xml", "https://blog.rust-lang.org"),
    # --- Crystal ---
    ("Crystal Blog (oficial)", "https://crystal-lang.org/feed.xml", "https://crystal-lang.org/blog"),
    # --- Zig ---
    ("Zig News (oficial)", "https://ziglang.org/news/index.xml", "https://ziglang.org/news"),
    ("Zig Devlog", "https://ziglang.org/devlog/index.xml", "https://ziglang.org/devlog"),
    ("Andrew Kelley (criador do Zig)", "https://andrewkelley.me/rss.xml", "https://andrewkelley.me"),
    ("Mitchell Hashimoto", "https://mitchellh.com/feed.xml", "https://mitchellh.com"),
    # ^ Criador do Vagrant/Terraform, hoje full-time em Zig. Ghostty (terminal) é escrito em Zig.
    ("Loris Cro (Zig core team)", "https://kristoff.it/blog/rss.xml", "https://kristoff.it"),
    # --- Lua ---
    ("Lua.org News", "https://www.lua.org/news.rss", "https://www.lua.org/news.html"),
    ("Lua Space (community blog)", "https://lua.space/feed", "https://lua.space"),
    # =========================================================================
    # ENGINEERING BLOGS (Big Tech)
    # =========================================================================
    ("Netflix Tech Blog", "https://netflixtechblog.com/feed", "https://netflixtechblog.com"),
    ("Cloudflare Blog", "https://blog.cloudflare.com/rss", "https://blog.cloudflare.com"),
    ("GitHub Engineering", "https://github.blog/engineering/feed/", "https://github.blog/engineering"),
    ("Stripe Engineering", "https://stripe.com/blog/engineering/feed", "https://stripe.com/blog/engineering"),
    ("Uber Engineering", "https://eng.uber.com/feed/", "https://eng.uber.com"),
    ("Spotify Engineering", "https://engineering.atspotify.com/feed/", "https://engineering.atspotify.com"),
    ("Dropbox Tech", "https://dropbox.tech/feed", "https://dropbox.tech"),
    ("Airbnb Engineering", "https://medium.com/feed/airbnb-engineering", "https://medium.com/airbnb-engineering"),
    ("LinkedIn Engineering", "https://engineering.linkedin.com/blog.rss.html", "https://engineering.linkedin.com/blog"),
    ("Fly.io Blog", "https://fly.io/blog/feed.xml", "https://fly.io/blog"),
    ("Figma Engineering", "https://www.figma.com/blog/section/engineering/feed/", "https://www.figma.com/blog/section/engineering"),
 
    # =========================================================================
    # LOW-LEVEL / SYSTEMS PROGRAMMING
    # =========================================================================
    # C puro, syscalls, alocação de memória, embedded, performance
    ("null program (Chris Wellons)", "https://nullprogram.com/feed/", "https://nullprogram.com"),
    ("Brendan Gregg", "https://www.brendangregg.com/blog/rss.xml", "https://www.brendangregg.com/blog"),
    ("Embedded Artistry", "https://embeddedartistry.com/feed/", "https://embeddedartistry.com"),
    ("Justine Tunney", "https://justine.lol/rss.xml", "https://justine.lol"),
    ("Casey Muratori", "https://caseymuratori.com/feed", "https://caseymuratori.com"),
    ("Phil Oppermann (OS in Rust)", "https://os.phil-opp.com/rss.xml", "https://os.phil-opp.com"),
 
    # =========================================================================
    # COMPILERS / LANGUAGE DESIGN / INTERPRETERS
    # =========================================================================
    # Parsers, VMs, JIT, garbage collection, design de linguagens
    ("Bob Nystrom (Crafting Interpreters)", "https://journal.stuffwithstuff.com/rss.xml", "https://journal.stuffwithstuff.com"),
    ("Russ Cox", "https://research.swtch.com/feed.atom", "https://research.swtch.com"),
    ("Laurence Tratt", "https://tratt.net/laurie/blog/blog.rss", "https://tratt.net/laurie/blog"),
 
    # =========================================================================
    # KERNEL / LINUX / OS INTERNALS
    # =========================================================================
    ("LWN.net", "https://lwn.net/headlines/rss", "https://lwn.net"),
    ("Phoronix", "https://www.phoronix.com/rss.php", "https://www.phoronix.com"),
    ("Linux Kernel Monkey Log (Greg KH)", "https://www.kroah.com/log/index.rss", "https://www.kroah.com/log"),
    ("OSnews", "https://www.osnews.com/feed/", "https://www.osnews.com"),
 
    # =========================================================================
    # RETRO COMPUTING / HISTÓRIA DO SOFTWARE
    # =========================================================================
    # Décadas passadas, arqueologia de código, hardware antigo, decisões de design históricas
    ("The Digital Antiquarian", "https://www.filfre.net/feed/", "https://www.filfre.net"),
    ("OS/2 Museum", "https://www.os2museum.com/wp/feed/", "https://www.os2museum.com"),
    ("Computer History Museum Blog", "https://computerhistory.org/blog/feed/", "https://computerhistory.org/blog"),
    ("Two-Bit History", "https://twobithistory.org/feed.xml", "https://twobithistory.org"),
    ("Retro Game Mechanics Explained", "https://www.youtube.com/feeds/videos.xml?channel_id=UCwRqWnW5ZkVaP_lZF7caZ-g", "https://www.youtube.com/@RGMechEx"),
    ("Fabien Sanglard", "https://fabiensanglard.net/rss.xml", "https://fabiensanglard.net"),
 
    # =========================================================================
    # SECURITY / REVERSE ENGINEERING
    # =========================================================================
    # Análise de binários, exploits, fuzzing — visão única do low-level
    ("Google Project Zero", "https://googleprojectzero.blogspot.com/feeds/posts/default", "https://googleprojectzero.blogspot.com"),
    ("Trail of Bits", "https://blog.trailofbits.com/feed/", "https://blog.trailofbits.com"),
 
    # =========================================================================
    # DEVS VETERANOS / BLOGS PESSOAIS
    # =========================================================================
    ("The Old New Thing (Raymond Chen)", "https://devblogs.microsoft.com/oldnewthing/feed", "https://devblogs.microsoft.com/oldnewthing"),
    ("Dan Luu", "https://danluu.com/atom.xml", "https://danluu.com"),
    ("Julia Evans", "https://jvns.ca/atom.xml", "https://jvns.ca"),
    ("Eli Bendersky", "https://eli.thegreenplace.net/feeds/all.atom.xml", "https://eli.thegreenplace.net"),
    ("Drew DeVault", "https://drewdevault.com/blog/index.xml", "https://drewdevault.com"),
    ("Martin Kleppmann", "https://martin.kleppmann.com/feed.xml", "https://martin.kleppmann.com"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/", "https://simonwillison.net"),
    ("Coding Horror (Jeff Atwood)", "https://blog.codinghorror.com/rss/", "https://blog.codinghorror.com"),
    ("Joel on Software", "https://www.joelonsoftware.com/feed/", "https://joelonsoftware.com"),
    ("Antirez (Salvatore Sanfilippo)", "http://antirez.com/rss", "http://antirez.com"),
    ("Marc Brooker", "https://brooker.co.za/blog/rss.xml", "https://brooker.co.za/blog"),
    ("Rachel by the Bay", "https://rachelbythebay.com/w/atom.xml", "https://rachelbythebay.com"),
    ("Ruslan Spivak", "https://ruslanspivak.com/feeds/all.atom.xml", "https://ruslanspivak.com"),
 
    # =========================================================================
    # AGREGADORES / COMUNIDADES
    # =========================================================================
    # ("Hacker News (Best)", "https://hnrss.org/best", "https://news.ycombinator.com"),
    # ("Lobsters", "https://lobste.rs/rss", "https://lobste.rs"),
 
    # =========================================================================
    # SITES / PUBLICAÇÕES TECH
    # =========================================================================
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab", "https://arstechnica.com"),
    ("InfoQ", "https://feed.infoq.com/", "https://infoq.com"),
    ("The New Stack", "https://thenewstack.io/feed/", "https://thenewstack.io"),
 
    # =========================================================================
    # BLOGS BR
    # =========================================================================
    ("Building Nubank", "https://building.nubank.com/feed/", "https://building.nubank.com"),
]


async def main():
    await Tortoise.init(
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["databases.models"]},
    )
    await Tortoise.generate_schemas()

    criados = 0
    for nome, url_rss, url_site in FEEDS:
        _, created = await Feed.get_or_create(
            url_rss=url_rss,
            defaults={"nome": nome, "url_site": url_site},
        )
        if created:
            criados += 1
            print(f"  + {nome}")
        else:
            print(f"  = {nome} (ja existe)")

    print(f"\n{criados} feeds criados, {len(FEEDS) - criados} ja existiam.")

    admin, admin_criado = await Admin.get_or_create(
        usuario="admin",
        defaults={"senha_hash": hash_senha("admin123")},
    )
    if admin_criado:
        print("\nAdmin criado: usuario=admin senha=admin123 (troque a senha!)")
    else:
        print("\nAdmin ja existe.")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
