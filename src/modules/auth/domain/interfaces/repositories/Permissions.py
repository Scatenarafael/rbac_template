from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities import Permission


class IPermissionsRepository(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def create(self, data: Permission) -> Permission:
        pass
