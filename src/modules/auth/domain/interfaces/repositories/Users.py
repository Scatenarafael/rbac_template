from abc import abstractmethod
from uuid import UUID

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class IUserRepository(IRepositoryBase[User, UUID]):
    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def change_password(self, id: UUID, new_password: str) -> User | None:
        raise NotImplementedError
