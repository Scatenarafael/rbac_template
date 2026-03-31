from uuid import UUID

from src.modules.auth.domain.entities import UserTenant
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class IUserTenantRepository(IRepositoryBase[UserTenant, UUID]):
    pass
