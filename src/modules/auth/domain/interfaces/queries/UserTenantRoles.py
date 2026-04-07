from abc import abstractmethod
from typing import Sequence
from uuid import UUID

from src.modules.auth.domain.entities import UserTenantRoleDetailed
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class IUserTenantRoleQuery(IQueryBase[UserTenantRoleDetailed, UUID]):
    @abstractmethod
    async def find_utr_by_user_and_tenant_id(self, user_id: UUID, tenant_id: UUID) -> Sequence[UserTenantRoleDetailed]:
        pass
