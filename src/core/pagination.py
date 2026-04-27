from collections.abc import Callable, Sequence
from typing import Generic, TypeVar, TypedDict

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

TEntity = TypeVar("TEntity")
TModel = TypeVar("TModel")

DEFAULT_PER_PAGE = 20


class PaginationMeta(TypedDict):
    perPage: int
    pageIndex: int


class PaginatedResult(TypedDict, Generic[TEntity]):
    meta: PaginationMeta
    results: list[TEntity]


ListResult = Sequence[TEntity] | PaginatedResult[TEntity]


async def paginate_query(
    session: AsyncSession,
    stmt: Select[tuple[TModel]],
    mapper: Callable[[TModel], TEntity],
    page: int | None = None,
    per_page: int = DEFAULT_PER_PAGE,
) -> ListResult[TEntity]:
    if page is None:
        result = await session.execute(stmt)
        return [mapper(model) for model in result.scalars().all()]

    result = await session.execute(stmt.limit(per_page).offset((page - 1) * per_page))

    return {
        "meta": {
            "perPage": per_page,
            "pageIndex": page,
        },
        "results": [mapper(model) for model in result.scalars().all()],
    }
