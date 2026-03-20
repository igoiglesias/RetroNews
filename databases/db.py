from config.config import DB_PATH

# aerich.models omitido intencionalmente — projeto usa generate_schemas=True
# sem migrations formais (ver spec para justificativa)
TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{DB_PATH}",
    },
    "apps": {
        "models": {
            "models": ["databases.models"],
            "default_connection": "default",
        },
    },
}
