import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, cast

from fastapi import Response
from jose import JWTError, jwt

from src.core.config.config import get_settings
from src.modules.auth.application.interfaces.services.HandleTokenService import IHandleTokenService
from src.modules.auth.domain.entities import RefreshToken
from src.modules.auth.domain.exceptions import InvalidCredentials, RefreshExpired, RefreshInvalid, RefreshReuseDetected
from src.modules.auth.domain.interfaces.repositories.RefreshTokens import IRefreshTokenRepository

# Access token (JWT)

settings = get_settings()


class HandleTokenService(IHandleTokenService):
    def __init__(self, refresh_token_repository: Optional[IRefreshTokenRepository]):
        self.refresh_token_repository = refresh_token_repository

    def _new_jti(self) -> str:
        return str(uuid.uuid4())

    # Refresh tokens (opaque)
    def _generate_refresh_token_raw(self):
        # gera um token opaco seguro + jti encodado dentro, mas vamos guardar jti separado no DB
        return secrets.token_urlsafe(64)

    def _hash_refresh_token(self, token: str) -> str:
        # usar sha256 — armazenamos o hash no DB
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _parse_jti(jti: str) -> uuid.UUID:
        try:
            return uuid.UUID(jti)
        except (TypeError, ValueError) as exc:
            raise RefreshInvalid("Identificador do refresh invalido") from exc

    async def create_access_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": user_id, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
        token = jwt.encode(payload, settings.ACCESS_SECRET, algorithm=settings.ALGORITHM)
        return token

    async def create_refresh_token(self, user_id: str) -> dict:

        # creating refresh token
        raw_refresh = self._generate_refresh_token_raw()
        refresh_hash = self._hash_refresh_token(raw_refresh)

        jti = self._new_jti()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        if self.refresh_token_repository:
            await self.refresh_token_repository.save_refresh_token(
                jti=uuid.UUID(jti),
                fk_user_id=uuid.UUID(user_id),
                token_hash=refresh_hash,
                expires_at=expires_at,
            )
        return {"refresh_token": raw_refresh, "refresh_jti": jti, "user_id": str(user_id)}

    @staticmethod
    async def verify_access_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.ACCESS_SECRET, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    async def rotate_refresh(self, raw_refresh: str, jti: str):
        # refreshing token
        if not self.refresh_token_repository:
            raise InvalidCredentials("Refresh token repository not available")

        record_model = await self.refresh_token_repository.get_by_jti(self._parse_jti(jti))

        if not record_model:
            raise InvalidCredentials("Refresh token não encontrado")

        record_model = cast(RefreshToken, record_model)

        if record_model.revoked:
            # recicling detected → lets revolke this user chain
            await self.refresh_token_repository.revoke_all_for_user(uuid.UUID(str(record_model.fk_user_id)))
            raise RefreshReuseDetected("Refresh reutilizado. Sessões revogadas.")

        # validates the hash securely
        if not hmac.compare_digest(record_model.token_hash, self._hash_refresh_token(raw_refresh)):
            await self.refresh_token_repository.revoke_all_for_user(uuid.UUID(str(record_model.fk_user_id)))
            raise RefreshInvalid("Refresh inválido. Sessões revogadas.")

        expires_at = record_model.expires_at if isinstance(record_model.expires_at, datetime) else datetime.fromisoformat(record_model.expires_at)

        if expires_at < datetime.now(timezone.utc):
            raise RefreshExpired("Refresh expirado")

        # revokes old refresh token
        await self.refresh_token_repository.revoke_all_for_user(uuid.UUID(str(record_model.fk_user_id)))
        # await self.refresh_token_repository.revoke_token(record_model, replaced_by=new_jti)

        # recicling should be done only if refresh_token is valid and not expired
        new_raw = self._generate_refresh_token_raw()
        new_hash = self._hash_refresh_token(new_raw)
        new_jti = self._new_jti()
        new_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # saving new refresh token
        await self.refresh_token_repository.save_refresh_token(
            jti=uuid.UUID(new_jti),
            fk_user_id=uuid.UUID(str(record_model.fk_user_id)),
            token_hash=new_hash,
            expires_at=new_expires,
        )

        # new access token
        new_access = await self.create_access_token(str(record_model.fk_user_id))

        return {
            "access_token": new_access,
            "refresh_token": new_raw,
            "refresh_jti": new_jti,
            "user_id": str(record_model.fk_user_id),
        }

    @staticmethod
    def set_access_cookie(response: Response, access_token: str) -> None:
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

    @staticmethod
    def set_refresh_cookie(response: Response, jti: str, raw_refresh: str) -> None:
        # expected cookie format: "<jti>:<raw_refresh>"
        cookie_value = f"{jti}:{raw_refresh}"
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=cookie_value,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=max_age,
            path="/",
        )

    @staticmethod
    def clear_cookies(response: Response) -> None:
        response.delete_cookie(settings.ACCESS_COOKIE_NAME)
        response.delete_cookie(settings.REFRESH_COOKIE_NAME)
