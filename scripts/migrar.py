"""
Adiciona colunas/tabelas novas ao banco existente sem perder dados.
Uso: make migrar
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise

from config.config import DB_PATH


async def main():
    await Tortoise.init(
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["databases.models"]},
    )
    conn = Tortoise.get_connection("default")

    # Helper: verificar se coluna existe
    async def coluna_existe(tabela: str, coluna: str) -> bool:
        info = await conn.execute_query_dict(f"PRAGMA table_info({tabela})")
        return any(c["name"] == coluna for c in info)

    # Helper: verificar se tabela existe
    async def tabela_existe(tabela: str) -> bool:
        rows = await conn.execute_query_dict(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            [tabela],
        )
        return len(rows) > 0

    alteracoes = 0

    # --- Noticia: novos campos ---
    if not await coluna_existe("noticia", "tentativas_ia"):
        await conn.execute_script("ALTER TABLE noticia ADD COLUMN tentativas_ia INT NOT NULL DEFAULT 0;")
        print("+ noticia.tentativas_ia")
        alteracoes += 1

    if not await coluna_existe("noticia", "erro_ia"):
        await conn.execute_script("ALTER TABLE noticia ADD COLUMN erro_ia TEXT;")
        print("+ noticia.erro_ia")
        alteracoes += 1

    # --- ConfigIA ---
    if not await tabela_existe("config_ia"):
        await conn.execute_script("""
            CREATE TABLE config_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave VARCHAR(100) NOT NULL UNIQUE,
                valor TEXT NOT NULL DEFAULT '',
                atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("+ tabela config_ia")
        alteracoes += 1

    # --- LogProcessamento ---
    if not await tabela_existe("log_processamento"):
        await conn.execute_script("""
            CREATE TABLE log_processamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo VARCHAR(50) NOT NULL DEFAULT '',
                mensagem TEXT NOT NULL DEFAULT '',
                detalhes TEXT,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("+ tabela log_processamento")
        alteracoes += 1

    # --- Indices ---
    try:
        await conn.execute_script(
            "CREATE INDEX IF NOT EXISTS idx_noticia_ia_data ON noticia (resumo_ia, data_publicacao);"
        )
        await conn.execute_script(
            "CREATE INDEX IF NOT EXISTS idx_noticia_feed_data ON noticia (feed_id, data_publicacao);"
        )
        await conn.execute_script(
            "CREATE INDEX IF NOT EXISTS idx_noticia_tentativas ON noticia (resumo_ia, tentativas_ia);"
        )
        print("+ indices otimizacao")
        alteracoes += 1
    except Exception as e:
        print(f"  indices: {e}")

    # --- WAL mode ---
    await conn.execute_script("PRAGMA journal_mode=WAL;")
    print("+ WAL mode ativado")

    if alteracoes:
        print(f"\n{alteracoes} alteracoes aplicadas.")
    else:
        print("\nBanco ja esta atualizado.")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
