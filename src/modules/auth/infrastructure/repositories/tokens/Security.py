# app/core/security.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.core.config.config import get_settings

# Access token (JWT)

settings = get_settings()


def create_access_token(subject: str):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    token = jwt.encode(payload, settings.ACCESS_SECRET, algorithm=settings.ALGORITHM)
    return token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# Refresh tokens (opaque)
def generate_refresh_token_raw():
    # gera um token opaco seguro + jti encodado dentro, mas vamos guardar jti separado no DB
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    # usar sha256 — armazenamos o hash no DB
    return hashlib.sha256(token.encode()).hexdigest()
