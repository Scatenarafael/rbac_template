from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.modules.auth.domain.exceptions import TenantAlreadyExists
from src.modules.auth.domain.entities.Tenant import Tenant
from src.modules.auth.domain.interfaces.repositories.Tenants import ITenantRepository
from src.modules.auth.infrastructure.mappers.TenantMappers import TenantMapper
from src.modules.auth.infrastructure.models.Tenant import TenantModel


class TenantsRepository(ITenantRepository):
    async def create(self, data: Tenant) -> Tenant:

        tenant = TenantMapper.from_entity(data)

        self._session.add(tenant)
        try:
            await self._session.flush()
            await self._session.refresh(tenant)
        except IntegrityError as exc:
            await self._session.rollback()
            raise TenantAlreadyExists("Tenant name already exists!") from exc

        return TenantMapper.to_entity(tenant)

    async def update(self, id: UUID, data: dict) -> Tenant | None:
        stmt = select(TenantModel).where(TenantModel.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if tenant is None:
            return None

        updatable_fields = {"name"}

        updated = False
        for field_name in updatable_fields:
            if field_name not in data:
                continue

            value = data[field_name]

            # Ignore explicit null to preserve current value on PATCH-like updates.
            if value is None:
                continue

            if getattr(tenant, field_name) != value:
                setattr(tenant, field_name, value)
                updated = True

        if updated:
            try:
                await self._session.commit()
                await self._session.refresh(tenant)
            except IntegrityError as exc:
                await self._session.rollback()
                raise TenantAlreadyExists("Tenant name already exists!") from exc

        return TenantMapper.to_entity(tenant)

    async def delete(self, id: UUID) -> None:
        try:
            await self._session.execute(delete(TenantModel).where(TenantModel.id == id))  # type: ignore
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
