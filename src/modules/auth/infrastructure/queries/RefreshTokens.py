from typing import Sequence
from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities import RefreshToken
from src.modules.auth.domain.interfaces.queries.RefreshTokens import IRefreshTokensQuery
from src.modules.auth.infrastructure.mappers.RefreshTokenMappers import RefreshTokenMapper
from src.modules.auth.infrastructure.models.RefreshToken import RefreshTokenModel


class RefreshTokensQuery(IRefreshTokensQuery):
    async def list(self) -> list[RefreshToken]:
        stmt = select(RefreshTokenModel)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        refresh_tokens = result.scalars().all()
        return [RefreshTokenMapper.to_entity(refresh_token) for refresh_token in refresh_tokens]

    async def get_by_id(self, id: UUID) -> RefreshToken | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            return None

        return RefreshTokenMapper.to_entity(refresh_token)

    async def find_by_user_id(self, user_id: UUID) -> Sequence[RefreshToken]:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.fk_user_id == user_id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        refresh_tokens = result.scalars().all()
        return [RefreshTokenMapper.to_entity(refresh_token) for refresh_token in refresh_tokens]
