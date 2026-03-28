from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.Permission import Permission


class IPermissionsRepository(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Permission:
        pass

    @abstractmethod
    async def create(self, data: Permission) -> Permission:
        pass
