from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")


class IRepositoryBase(ABC, Generic[TEntity, TId]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def create(self, data: TEntity) -> TEntity:
        pass

    @abstractmethod
    async def update(self, id: TId, data: dict) -> TEntity | None:
        pass

    @abstractmethod
    async def delete(self, id: TId) -> None:
        pass
