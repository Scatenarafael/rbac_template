from uuid import UUID

from sqlalchemy import delete, select

from src.modules.auth.domain.entities import LinkUserTenantRequest, UserTenant, UserTenantRole
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.interfaces.repositories.LinkUserTenantRequest import ILinkUserTenantRequestRepository
from src.modules.auth.infrastructure.mappers.LinkUserTenantRequestMappers import LinkUserTenantRequestMapper
from src.modules.auth.infrastructure.mappers.UserTenantMappers import UserTenantMapper
from src.modules.auth.infrastructure.mappers.UserTenantRoleMappers import UserTenantRoleMapper
from src.modules.auth.infrastructure.models import LinkUserTenantRequestModel
from src.modules.auth.infrastructure.models.Role import RoleModel


class LinkUserTenantRequestRepository(ILinkUserTenantRequestRepository):
    async def create(self, data: LinkUserTenantRequest) -> LinkUserTenantRequest:
        link_user_tenant_request_model = LinkUserTenantRequestMapper.from_entity(data)

        self._session.add(link_user_tenant_request_model)
        await self._session.commit()
        await self._session.refresh(link_user_tenant_request_model)
        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)

    async def get_by_id(self, id: UUID) -> LinkUserTenantRequest | None:

        stmt = select(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        link_user_tenant_request_model = result.scalar_one_or_none()

        if link_user_tenant_request_model is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)

    async def update(self, id: UUID, data: dict) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        link_user_tenant_request_model = result.scalar_one_or_none()

        if link_user_tenant_request_model is None:
            return None

        updatable_fields = {
            "status": "",
        }

        updated = False
        for field_name, default_value in updatable_fields.items():
            value = getattr(data, field_name, default_value)

            # Treat entity default values as "not provided" for partial updates.
            if value is None:
                continue
            if value == default_value:
                continue

            setattr(link_user_tenant_request_model, field_name, value)
            updated = True

        if not updated:
            return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)

        self._session.add(link_user_tenant_request_model)
        await self._session.commit()
        await self._session.refresh(link_user_tenant_request_model)

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)

    async def delete(self, id: UUID) -> None:
        stmt = delete(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore

        await self._session.execute(stmt)
        await self._session.commit()

    async def approve(self, id: UUID) -> LinkUserTenantRequest | None:
        select_stmt = select(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore

        select_member_role_stmt = select(RoleModel).where(RoleModel.name == "member")  # type: ignore

        result = await self._session.execute(select_stmt)
        link_user_tenant_request_model = result.scalar_one_or_none()

        if link_user_tenant_request_model is None:
            return None

        user_tenant_model = UserTenantMapper.from_entity(
            UserTenant(
                fk_user_id=link_user_tenant_request_model.fk_user_id,
                fk_tenant_id=link_user_tenant_request_model.fk_tenant_id,
            )
        )

        if select_member_role_stmt is not None:
            user_tenant_role_model = UserTenantRoleMapper.from_entity(
                UserTenantRole(
                    fk_user_tenant_id=user_tenant_model.id,
                    fk_role_id=select_member_role_stmt.scalar_one().id,  # type: ignore
                )
            )
            self._session.add(user_tenant_role_model)

        link_user_tenant_request_model.status = LinkUserTenantRequestStatus.APPROVED

        self._session.add(user_tenant_model)
        self._session.add(link_user_tenant_request_model)
        await self._session.commit()
        await self._session.refresh(link_user_tenant_request_model)

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)

    async def reject(self, id: UUID) -> LinkUserTenantRequest | None:
        select_stmt = select(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore

        result = await self._session.execute(select_stmt)
        link_user_tenant_request_model = result.scalar_one_or_none()

        if link_user_tenant_request_model is None:
            return None

        link_user_tenant_request_model.status = LinkUserTenantRequestStatus.REJECTED
        self._session.add(link_user_tenant_request_model)
        await self._session.commit()
        await self._session.refresh(link_user_tenant_request_model)

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request_model)
