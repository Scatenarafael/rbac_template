from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import DEFAULT_PER_PAGE, ListResult

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")


class IQueryBase(ABC, Generic[TEntity, TId]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[TEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, id: TId) -> TEntity | None:
        pass
