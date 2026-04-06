from uuid import UUID

from src.modules.auth.domain.entities import Permission
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class IPermissionsQuery(IQueryBase[Permission, UUID]):
    pass
