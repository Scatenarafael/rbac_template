from uuid import UUID

from src.modules.auth.domain.entities import Role
from src.modules.auth.domain.interfaces.repositories.Base import IRepositoryBase


class IRolesRepository(IRepositoryBase[Role, UUID]):
    pass
