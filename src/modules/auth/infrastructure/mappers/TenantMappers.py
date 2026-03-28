from uuid import UUID

from src.modules.auth.domain.entities.Tenant import Tenant
from src.modules.auth.infrastructure.models.Tenant import TenantModel


class TenantMapper:
    @staticmethod
    def to_entity(model: TenantModel) -> Tenant:
        return Tenant(id=UUID(str(model.id)), name=str(model.name))

    @staticmethod
    def from_entity(entity: Tenant) -> TenantModel:

        return TenantModel(id=entity.id, name=entity.name)
