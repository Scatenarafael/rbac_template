from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update

from src.modules.auth.domain.entities import RefreshToken
from src.modules.auth.domain.interfaces.repositories.RefreshTokens import IRefreshTokenRepository
from src.modules.auth.infrastructure.mappers.RefreshTokenMappers import RefreshTokenMapper
from src.modules.auth.infrastructure.models.RefreshToken import RefreshTokenModel


class RefreshTokenRepository(IRefreshTokenRepository):
    async def save_refresh_token(self, jti: UUID, fk_user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken | None:
        refresh_token = RefreshTokenModel(id=jti, fk_user_id=fk_user_id, token_hash=token_hash, expires_at=expires_at)
        self._session.add(refresh_token)
        await self._session.commit()
        await self._session.refresh(refresh_token)
        return RefreshTokenMapper.to_entity(refresh_token)

    async def revoke_token_by_jti(self, jti: UUID, replaced_by: str | None = None) -> None:

        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == jti)  # type: ignore

        result = await self._session.execute(stmt)

        token = result.scalars().first()

        if token is None:
            return

        token.revoke(replaced_by=replaced_by)

        await self._session.commit()
        await self._session.refresh(token)

    async def delete_token_by_jti(self, jti: UUID) -> None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == jti)  # type: ignore
        result = await self._session.execute(stmt)
        token = result.scalars().first()
        if token:
            await self._session.delete(token)
            await self._session.commit()

    async def revoke_all_for_user(self, fk_user_id: str) -> None:
        stmt = update(RefreshTokenModel).where(RefreshTokenModel.fk_user_id == fk_user_id, RefreshTokenModel.revoked.is_(False)).values(revoked=True)  # type: ignore
        await self._session.execute(stmt)
        await self._session.commit()

    async def revoke_token(self, jti: UUID, replaced_by: str | None = None) -> None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == jti)  # type: ignore
        result = await self._session.execute(stmt)
        token = result.scalars().first()
        if token:
            token.revoke(replaced_by=replaced_by)
            await self._session.commit()
            await self._session.refresh(token)

    async def delete_token(self, jti: UUID) -> None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == jti)  # type: ignore
        result = await self._session.execute(stmt)
        token = result.scalars().first()
        if token:
            await self._session.delete(token)
            await self._session.commit()
