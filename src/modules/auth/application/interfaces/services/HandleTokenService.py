from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")


class IHandleTokenService(ABC, Generic[TResponse]):
    @abstractmethod
    async def create_access_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    async def create_refresh_token(self, user_id: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    async def verify_access_token(token: str) -> dict | None:
        pass

    @abstractmethod
    async def rotate_refresh(self, raw_refresh: str, jti: str) -> dict | None:
        pass

    @staticmethod
    @abstractmethod
    def set_access_cookie(response: TResponse, access_token: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def set_refresh_cookie(response: TResponse, jti: str, raw_refresh: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def clear_cookies(response: TResponse) -> None:
        pass
