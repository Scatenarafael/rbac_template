from uuid import UUID

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.interfaces.queries.Base import IQueryBase


class ILinkUserTenantRequestsQuery(IQueryBase[LinkUserTenantRequest, UUID]):
    pass
