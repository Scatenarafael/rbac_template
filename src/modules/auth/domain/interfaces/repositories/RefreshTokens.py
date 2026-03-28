from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities import RefreshToken


class IRefreshTokenRepository(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def save_refresh_token(self, jti: UUID, fk_user_tenant_id: UUID, token_hash: str, expires_at: datetime) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def get_by_jti(self, jti: UUID) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def revoke_token(self, jti: UUID, replaced_by: str | None = None) -> None:
        pass

    @abstractmethod
    async def delete_token(self, jti: UUID) -> None:
        pass

    @abstractmethod
    async def revoke_all_for_user_tenant(self, fk_user_tenant_id: UUID) -> None:
        pass
