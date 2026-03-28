from uuid import UUID

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import (
    LinkUserTenantRequestStatus,
)
from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel


class LinkUserTenantRequestMapper:
    @staticmethod
    def to_entity(model: LinkUserTenantRequestModel) -> LinkUserTenantRequest:
        return LinkUserTenantRequest(
            id=UUID(str(model.id)),
            fk_tenant_id=UUID(str(model.fk_tenant_id)),
            fk_user_id=UUID(str(model.fk_user_id)),
            status=LinkUserTenantRequestStatus(model.status),
        )

    @staticmethod
    def from_entity(entity: LinkUserTenantRequest) -> LinkUserTenantRequestModel:

        return LinkUserTenantRequestModel(
            id=entity.id,
            fk_tenant_id=entity.fk_tenant_id,
            fk_user_id=entity.fk_user_id,
            status=entity.status,
        )
