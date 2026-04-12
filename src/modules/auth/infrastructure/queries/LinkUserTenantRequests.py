from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.entities.LinkUserTenantRequest import LinkUserTenantRequestDetailed
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.infrastructure.mappers.LinkUserTenantRequestMappers import LinkUserTenantRequestMapper
from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel


class LinkUserTenantRequestsQuery(ILinkUserTenantRequestsQuery):
    async def list(self) -> list[LinkUserTenantRequest]:
        stmt = select(LinkUserTenantRequestModel)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        link_user_tenant_requests = result.scalars().all()
        return [LinkUserTenantRequestMapper.to_entity(link_user_tenant_request) for link_user_tenant_request in link_user_tenant_requests]

    async def get_by_id(self, id: UUID) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(LinkUserTenantRequestModel.id == id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)

    async def list_by_tenant_id(self, tenant_id: UUID) -> Sequence[LinkUserTenantRequestDetailed]:
        stmt = select(LinkUserTenantRequestModel).options(selectinload(LinkUserTenantRequestModel.user)).where(LinkUserTenantRequestModel.fk_tenant_id == tenant_id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        link_user_tenant_requests = result.scalars().all()
        return [LinkUserTenantRequestMapper.to_detailed_entity(link_user_tenant_request) for link_user_tenant_request in link_user_tenant_requests]

    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(  # type: ignore[arg-type]
            LinkUserTenantRequestModel.fk_tenant_id == tenant_id,
            LinkUserTenantRequestModel.fk_user_id == user_id,
            LinkUserTenantRequestModel.status == LinkUserTenantRequestStatus.PENDING,
        )
        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)
