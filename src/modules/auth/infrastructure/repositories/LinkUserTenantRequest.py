from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestStatus
from src.modules.auth.domain.exceptions import LinkUserTenantRequestAlreadyPending
from src.modules.auth.domain.interfaces.repositories.LinkUserTenantRequest import ILinkUserTenantRequestRepository
from src.modules.auth.infrastructure.mappers.LinkUserTenantRequestMappers import LinkUserTenantRequestMapper
from src.modules.auth.infrastructure.models import LinkUserTenantRequestModel


class LinkUserTenantRequestRepository(ILinkUserTenantRequestRepository):
    async def create(self, data: LinkUserTenantRequest) -> LinkUserTenantRequest:
        link_user_tenant_request_model = LinkUserTenantRequestMapper.from_entity(data)

        self._session.add(link_user_tenant_request_model)
        try:
            await self._session.commit()
            await self._session.refresh(link_user_tenant_request_model)
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_pending_link_user_tenant_request_duplicate(exc):
                raise LinkUserTenantRequestAlreadyPending("There is already a pending tenant request for this user!") from exc
            raise

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

        result = await self._session.execute(select_stmt)
        link_user_tenant_request_model = result.scalar_one_or_none()

        if link_user_tenant_request_model is None:
            return None

        link_user_tenant_request_model.status = LinkUserTenantRequestStatus.APPROVED

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


def _is_pending_link_user_tenant_request_duplicate(exc: IntegrityError) -> bool:
    return "uq_link_user_tenant_requests_tenant_user_status" in str(exc)
