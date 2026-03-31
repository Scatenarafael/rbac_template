from src.modules.auth.domain.entities import Tenant
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema


class TenantCreationPayloadDTO:
    @staticmethod
    def to_entity(payload: TenantCreationPayloadSchema):
        return Tenant(
            name=payload.name,
        )
