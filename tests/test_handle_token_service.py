import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from src.modules.auth.domain.entities.RefreshToken import RefreshToken
from src.modules.auth.domain.exceptions import InvalidCredentials, RefreshExpired, RefreshInvalid, RefreshReuseDetected
from src.modules.auth.infrastructure.services.HandleTokenService import HandleTokenService


class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self.revoke_all_calls = []
        self.save_calls = []

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        self.revoke_all_calls.append(user_id)

    async def save_refresh_token(self, *, jti: UUID, fk_user_id: UUID, token_hash: str, expires_at: datetime) -> None:
        self.save_calls.append(
            {
                "jti": jti,
                "fk_user_id": fk_user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        )


class FakeRefreshTokensQuery:
    def __init__(self, record: RefreshToken | None = None) -> None:
        self.record = record
        self.get_by_id_calls = []

    async def get_by_id(self, id: UUID):
        self.get_by_id_calls.append(id)
        return self.record


def make_refresh_token(*, token_hash: str, fk_user_id: UUID | None = None, revoked: bool = False, expires_at: datetime | None = None) -> RefreshToken:
    return RefreshToken(
        id=uuid4(),
        token_hash=token_hash,
        fk_user_id=fk_user_id or uuid4(),
        revoked=revoked,
        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(days=1)),
    )


def test_rotate_refresh_requires_repository_configuration():
    service = HandleTokenService(refresh_token_repository=None)

    with pytest.raises(InvalidCredentials, match="Refresh token repository not available"):
        asyncio.run(service.rotate_refresh("opaque-refresh-token", str(uuid4())))


def test_rotate_refresh_revokes_all_sessions_when_refresh_is_reused():
    service = HandleTokenService(refresh_token_repository=None)
    user_id = uuid4()
    repository = FakeRefreshTokenRepository()
    refresh_tokens_query = FakeRefreshTokensQuery(
        make_refresh_token(
            token_hash=service._hash_refresh_token("opaque-refresh-token"),
            fk_user_id=user_id,
            revoked=True,
        )
    )
    service = HandleTokenService(refresh_token_repository=repository, refresh_tokens_query=refresh_tokens_query)

    with pytest.raises(RefreshReuseDetected, match="Refresh reutilizado"):
        asyncio.run(service.rotate_refresh("opaque-refresh-token", str(uuid4())))

    assert repository.revoke_all_calls == [user_id]


def test_rotate_refresh_revokes_all_sessions_when_hash_does_not_match():
    user_id = uuid4()
    repository = FakeRefreshTokenRepository()
    refresh_tokens_query = FakeRefreshTokensQuery(
        make_refresh_token(
            token_hash=HandleTokenService(refresh_token_repository=None)._hash_refresh_token("different-token"),
            fk_user_id=user_id,
        )
    )
    service = HandleTokenService(refresh_token_repository=repository, refresh_tokens_query=refresh_tokens_query)

    with pytest.raises(RefreshInvalid, match="Refresh invalido|Refresh inválido"):
        asyncio.run(service.rotate_refresh("opaque-refresh-token", str(uuid4())))

    assert repository.revoke_all_calls == [user_id]


def test_rotate_refresh_rejects_expired_token_without_rotating():
    user_id = uuid4()
    repository = FakeRefreshTokenRepository()
    refresh_tokens_query = FakeRefreshTokensQuery(
        make_refresh_token(
            token_hash=HandleTokenService(refresh_token_repository=None)._hash_refresh_token("opaque-refresh-token"),
            fk_user_id=user_id,
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
    )
    service = HandleTokenService(refresh_token_repository=repository, refresh_tokens_query=refresh_tokens_query)

    with pytest.raises(RefreshExpired, match="Refresh expirado"):
        asyncio.run(service.rotate_refresh("opaque-refresh-token", str(uuid4())))

    assert repository.revoke_all_calls == []
    assert repository.save_calls == []


def test_rotate_refresh_revokes_old_token_saves_new_one_and_returns_new_credentials():
    user_id = uuid4()
    raw_refresh = "opaque-refresh-token"
    repository = FakeRefreshTokenRepository()
    refresh_tokens_query = FakeRefreshTokensQuery(
        make_refresh_token(
            token_hash=HandleTokenService(refresh_token_repository=None)._hash_refresh_token(raw_refresh),
            fk_user_id=user_id,
        )
    )
    service = HandleTokenService(refresh_token_repository=repository, refresh_tokens_query=refresh_tokens_query)
    refresh_jti = uuid4()

    result = asyncio.run(service.rotate_refresh(raw_refresh, str(refresh_jti)))

    assert refresh_tokens_query.get_by_id_calls == [refresh_jti]
    assert repository.revoke_all_calls == [user_id]
    assert len(repository.save_calls) == 1
    assert repository.save_calls[0]["fk_user_id"] == user_id
    assert repository.save_calls[0]["token_hash"] != raw_refresh
    assert result["user_id"] == str(user_id)
    assert result["refresh_token"] != raw_refresh
    assert UUID(result["refresh_jti"])
    assert isinstance(result["access_token"], str)


def test_create_refresh_token_persists_hashed_refresh_value():
    repository = FakeRefreshTokenRepository()
    service = HandleTokenService(refresh_token_repository=repository)
    user_id = uuid4()

    result = asyncio.run(service.create_refresh_token(str(user_id)))

    assert len(repository.save_calls) == 1
    assert repository.save_calls[0]["fk_user_id"] == user_id
    assert repository.save_calls[0]["token_hash"] != result["refresh_token"]
    assert repository.save_calls[0]["jti"] == UUID(result["refresh_jti"])
