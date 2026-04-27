from typing import Generic, TypeVar

from pydantic import BaseModel

TResult = TypeVar("TResult")


class PaginationMetaResponseBody(BaseModel):
    perPage: int
    pageIndex: int


class PaginatedResponseBody(BaseModel, Generic[TResult]):
    meta: PaginationMetaResponseBody
    results: list[TResult]
