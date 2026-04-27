from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import DEFAULT_PER_PAGE, ListResult
from src.modules.auth.application.rules import TenantRules
from src.modules.auth.domain.entities import Tenant, User, UserTenant, UserTenantRole
from src.modules.auth.domain.exceptions import ConfigurationError
from src.modules.auth.domain.interfaces.queries.Roles import IRolesQuery
from src.modules.auth.domain.interfaces.queries.Tenants import ITenantsQuery
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.repositories.Tenants import ITenantRepository
from src.modules.auth.domain.interfaces.repositories.UserTenantRoles import IUserTenantRoleRepository
from src.modules.auth.domain.interfaces.repositories.UserTenants import IUserTenantRepository
from src.modules.auth.presentation.schemas.dtos.tenant_dto import TenantCreationPayloadDTO
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema


class CreateTenantUseCase:
    def __init__(
        self,
        session: AsyncSession,
        tenant_repository: ITenantRepository,
        user_tenant_repository: IUserTenantRepository,
        user_tenant_role_repository: IUserTenantRoleRepository,
        tenants_query: ITenantsQuery,
        users_query: IUsersQuery,
        roles_query: IRolesQuery,
        rules: TenantRules,
    ) -> None:
        self.session = session
        self.tenant_repository = tenant_repository
        self.user_tenant_repository = user_tenant_repository
        self.user_tenant_role_repository = user_tenant_role_repository
        self.tenants_query = tenants_query
        self.users_query = users_query
        self.roles_query = roles_query
        self.rules = rules

    async def _create_tenant_relationships(self, user: User, tenant: Tenant) -> None:
        user_tenant = UserTenant(fk_user_id=user.id, fk_tenant_id=tenant.id)

        # Create user-tenant relationship
        user_tenant_instance = await self.user_tenant_repository.create(data=user_tenant)

        owner_role = await self.roles_query.find_by_name("tenantadmin")

        if not owner_role:
            raise ConfigurationError("Default role 'tenantadmin' not found. Please ensure it exists in the database.")

        user_tenant_role = UserTenantRole(fk_user_tenant_id=user_tenant_instance.id, fk_role_id=owner_role.id)

        # Assign default role to the user for the tenant (e.g., "admin")
        await self.user_tenant_role_repository.create(data=user_tenant_role)

    async def execute(self, payload: TenantCreationPayloadSchema, user_id: UUID) -> Tenant:
        user = await self.rules.validate_tenant_creation(payload.name, user_id)
        tenant = TenantCreationPayloadDTO.to_entity(payload)
        try:
            tenant = await self.tenant_repository.create(tenant)
            await self._create_tenant_relationships(user, tenant)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return tenant


class ListTenantsUseCase:
    def __init__(self, tenants_query: ITenantsQuery) -> None:
        self.tenants_query = tenants_query

    async def execute(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[Tenant]:
        if page is None:
            return await self.tenants_query.list()

        return await self.tenants_query.list(page=page, per_page=per_page)


class UpdateTenantUseCase:
    def __init__(self, tenant_repository: ITenantRepository, tenants_query: ITenantsQuery, rules: TenantRules) -> None:
        self.tenant_repository = tenant_repository
        self.tenants_query = tenants_query
        self.rules = rules

    async def execute(self, tenant_id: UUID, payload: TenantCreationPayloadSchema, logged_user_id: UUID) -> Optional[Tenant]:

        await self.rules.validate_tenant_update(tenant_id, payload.model_dump(), logged_user_id)

        return await self.tenant_repository.update(id=tenant_id, data=payload.model_dump())


class DeleteTenantUseCase:
    def __init__(self, tenant_repository: ITenantRepository, rules: TenantRules) -> None:
        self.tenant_repository = tenant_repository
        self.rules = rules

    async def execute(self, tenant_id: UUID, logged_user_id: UUID) -> None:
        await self.rules.validate_tenant_deletion(tenant_id, logged_user_id)
        await self.tenant_repository.delete(id=tenant_id)
