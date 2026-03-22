import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
DB_PATH = RAIZ / os.getenv("DB_PATH", "databases/db.sqlite3")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
APP_TITLE = os.getenv("APP_TITLE", "RetroNews")
APP_DEBUG = os.getenv("APP_DEBUG", "False") == "True"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
SCHEDULER_INTERVALO_MINUTOS = int(os.getenv("SCHEDULER_INTERVALO_MINUTOS", "60"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")
JWT_SECRET = os.getenv("JWT_SECRET", "retronews-jwt-secret-change-me")
JWT_EXPIRA_HORAS = int(os.getenv("JWT_EXPIRA_HORAS", "8"))
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False") == "True"
MAX_TENTATIVAS_IA = int(os.getenv("MAX_TENTATIVAS_IA", "3"))
OPENROUTER_ALERTA_CREDITOS = float(os.getenv("OPENROUTER_ALERTA_CREDITOS", "1.0"))
