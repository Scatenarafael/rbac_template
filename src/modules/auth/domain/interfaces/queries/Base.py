from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")


class IQueryBase(ABC, Generic[TEntity, TId]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def list(self) -> Sequence[TEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, id: TId) -> TEntity | None:
        pass
