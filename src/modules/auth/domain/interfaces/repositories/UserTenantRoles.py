from uuid import UUID

from src.modules.auth.domain.entities import UserTenantRole
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class IUserTenantRoleRepository(IRepositoryBase[UserTenantRole, UUID]):
    pass
