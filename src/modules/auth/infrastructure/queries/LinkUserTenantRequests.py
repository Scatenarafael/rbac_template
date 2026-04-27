from typing import cast, overload
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import col

from src.core.pagination import DEFAULT_PER_PAGE, ListResult, paginate_query
from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.entities.LinkUserTenantRequest import LinkTenantRequestDetailed, LinkUserTenantRequestDetailed
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.infrastructure.mappers.LinkUserTenantRequestMappers import LinkUserTenantRequestMapper
from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel
from src.modules.auth.infrastructure.models.Tenant import TenantModel
from src.modules.auth.infrastructure.models.User import UserModel


class LinkUserTenantRequestsQuery(ILinkUserTenantRequestsQuery):
    async def list(self, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkUserTenantRequest]:
        stmt = select(LinkUserTenantRequestModel)  # type: ignore[arg-type]
        return await paginate_query(self._session, stmt, LinkUserTenantRequestMapper.to_entity, page, per_page)

    async def get_by_id(self, id: UUID) -> LinkUserTenantRequest | None:
        stmt = select(LinkUserTenantRequestModel).where(col(LinkUserTenantRequestModel.id) == id)
        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)

    async def list_by_tenant_id(self, tenant_id: UUID, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkUserTenantRequestDetailed]:
        stmt = select(LinkUserTenantRequestModel).options(selectinload(cast(QueryableAttribute[UserModel], LinkUserTenantRequestModel.user))).where(col(LinkUserTenantRequestModel.fk_tenant_id) == tenant_id)
        return await paginate_query(self._session, stmt, LinkUserTenantRequestMapper.to_user_detailed_entity, page, per_page)

    @overload
    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID, page: None = None) -> LinkUserTenantRequest | None:
        ...

    @overload
    async def find_pending_by_tenant_and_user(self, tenant_id: UUID, user_id: UUID, page: int, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkUserTenantRequest]:
        ...

    async def find_pending_by_tenant_and_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        page: int | None = None,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> LinkUserTenantRequest | None | ListResult[LinkUserTenantRequest]:
        stmt = select(LinkUserTenantRequestModel).where(
            col(LinkUserTenantRequestModel.fk_tenant_id) == tenant_id,
            col(LinkUserTenantRequestModel.fk_user_id) == user_id,
            col(LinkUserTenantRequestModel.status) == LinkUserTenantRequestStatus.PENDING,
        )

        if page is not None:
            return await paginate_query(self._session, stmt, LinkUserTenantRequestMapper.to_entity, page, per_page)

        result = await self._session.execute(stmt)
        link_user_tenant_request = result.scalar_one_or_none()

        if link_user_tenant_request is None:
            return None

        return LinkUserTenantRequestMapper.to_entity(link_user_tenant_request)

    async def find_pending_by_user(self, user_id: UUID, page: int | None = None, per_page: int = DEFAULT_PER_PAGE) -> ListResult[LinkTenantRequestDetailed]:
        stmt = (
            select(LinkUserTenantRequestModel)
            .options(selectinload(cast(QueryableAttribute[TenantModel], LinkUserTenantRequestModel.tenant)))
            .where(
                col(LinkUserTenantRequestModel.fk_user_id) == user_id,
                col(LinkUserTenantRequestModel.status) == LinkUserTenantRequestStatus.PENDING,
            )
        )
        return await paginate_query(self._session, stmt, LinkUserTenantRequestMapper.to_tenant_detailed_entity, page, per_page)
