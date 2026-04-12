from typing import Sequence, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import col

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.entities.LinkUserTenantRequest import LinkTenantRequestDetailed, LinkUserTenantRequestDetailed
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.infrastructure.mappers.LinkUserTenantRequestMappers import LinkUserTenantRequestMapper
from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel
from src.modules.auth.infrastructure.models.Tenant import TenantModel
from src.modules.auth.infrastructure.models.User import UserModel


class LinkUserTenantRequestsQuery(ILinkUserTenantRequestsQuery):
    async def list(self) -> list[LinkUserTenantRequest]:
        stmt = select(LinkUserTenantRequestModel)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        link_user_tenant_requests = result.scalars().all()
        return [LinkUserTenantRequestMapper.to_entity(link_user_tenant_request) for link_user_tenant_request in link_user_tenant_requests]

    async def get_by_id(self, id: UUID) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(col(LinkUserTenantRequestModel.id) == id)
        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)

    async def list_by_tenant_id(self, tenant_id: UUID) -> Sequence[LinkUserTenantRequestDetailed]:
        stmt = select(LinkUserTenantRequestModel).options(selectinload(cast(QueryableAttribute[UserModel], LinkUserTenantRequestModel.user))).where(col(LinkUserTenantRequestModel.fk_tenant_id) == tenant_id)
        result = await self._session.execute(stmt)
        link_user_tenant_requests = result.scalars().all()
        return [LinkUserTenantRequestMapper.to_user_detailed_entity(link_user_tenant_request) for link_user_tenant_request in link_user_tenant_requests]

    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(
            col(LinkUserTenantRequestModel.fk_tenant_id) == tenant_id,
            col(LinkUserTenantRequestModel.fk_user_id) == user_id,
            col(LinkUserTenantRequestModel.status) == LinkUserTenantRequestStatus.PENDING,
        )
        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)

    async def find_pending_by_user(self, user_id: UUID) -> Sequence[LinkTenantRequestDetailed] | None:
        stmt = (
            select(LinkUserTenantRequestModel)
            .options(selectinload(cast(QueryableAttribute[TenantModel], LinkUserTenantRequestModel.tenant)))
            .where(
                col(LinkUserTenantRequestModel.fk_user_id) == user_id,
                col(LinkUserTenantRequestModel.status) == LinkUserTenantRequestStatus.PENDING,
            )
        )
        result = await self._session.execute(stmt)
        link_user_tenant_requests = result.scalars().all()

        if not link_user_tenant_requests:
            return None

        return [LinkUserTenantRequestMapper.to_tenant_detailed_entity(link_user_tenant_request) for link_user_tenant_request in link_user_tenant_requests]
