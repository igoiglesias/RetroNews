import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Request

from config.config import JWT_EXPIRA_HORAS, JWT_SECRET

_csrf_secret = secrets.token_hex(32)


# ── CSRF ──

def gerar_csrf_token(session_id: str) -> str:
    timestamp = str(int(time.time()))
    payload = f"{session_id}:{timestamp}"
    sig = hmac.new(_csrf_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{timestamp}:{sig}"


def validar_csrf_token(token: str, session_id: str) -> bool:
    if not token or ":" not in token:
        return False

    try:
        timestamp, sig = token.split(":", 1)
        payload = f"{session_id}:{timestamp}"
        esperado = hmac.new(_csrf_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]

        if not hmac.compare_digest(sig, esperado):
            return False

        if time.time() - int(timestamp) > 3600:
            return False

        return True
    except (ValueError, TypeError):
        return False


# ── IP ──

def obter_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


# ── Senha (bcrypt) ──

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


# ── JWT ──

def gerar_jwt(usuario: str) -> str:
    payload = {
        "sub": usuario,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRA_HORAS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def validar_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# ── Anti-spam ──

def detectar_spam(texto: str) -> bool:
    if not texto:
        return False

    texto_lower = texto.lower()

    if texto_lower.count("http") > 3:
        return True

    spam_words = ["casino", "viagra", "crypto", "free money", "click here", "buy now", "earn money"]
    for word in spam_words:
        if word in texto_lower:
            return True

    if len(texto.strip()) < 3 or len(texto) > 5000:
        return True

    return False
