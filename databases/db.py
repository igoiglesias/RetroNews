from config.config import DB_PATH

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": str(DB_PATH),
                "journal_mode": "WAL",
            },
        },
    },
    "apps": {
        "models": {
            "models": ["databases.models"],
            "default_connection": "default",
        },
    },
}
