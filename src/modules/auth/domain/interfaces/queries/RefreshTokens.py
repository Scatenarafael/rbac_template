from abc import abstractmethod
from typing import Sequence
from uuid import UUID

from src.modules.auth.domain.entities import RefreshToken
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class IRefreshTokensQuery(IQueryBase[RefreshToken, UUID]):
    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> Sequence[RefreshToken]:
        pass
