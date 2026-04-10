from uuid import UUID

from src.modules.auth.domain.entities import LinkUserTenantRequest, LinkUserTenantRequestDetailed, UserToLinkUserTenantRequestList
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

    @staticmethod
    def to_detailed_entity(model: LinkUserTenantRequestModel) -> LinkUserTenantRequestDetailed:
        return LinkUserTenantRequestDetailed(
            id=UUID(str(model.id)),
            user=UserToLinkUserTenantRequestList(
                id=UUID(str(model.user.id)),
                first_name=model.user.first_name,
                last_name=model.user.last_name,
                email=model.user.email,
            ),
            status=LinkUserTenantRequestStatus(model.status),
            updated_at=model.updated_at,
        )
