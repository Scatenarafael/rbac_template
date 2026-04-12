from typing import Optional
from uuid import UUID

from src.core.logging import get_logger
from src.modules.auth.application.rules.common.utils import CommonRules
from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestType
from src.modules.auth.domain.exceptions import (
    ConflictError,
    ForbiddenError,
    LinkUserTenantRequestAlreadyPending,
    NotFoundError,
    ValidationError,
)
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery

logger = get_logger(__name__)


class LinkUserTenantRequestsRules:
    def __init__(self, users_query: IUsersQuery, user_tenant_role_query: IUserTenantRoleQuery, link_user_tenant_request_query: ILinkUserTenantRequestsQuery):
        self.users_query = users_query
        self.user_tenant_role_query = user_tenant_role_query
        self.link_user_tenant_request_query = link_user_tenant_request_query

    async def validate_list_link_user_tenant_requests(self, tenant_id: UUID, authenticated_user_id: UUID):
        logger.debug(
            "Validating link user tenant request listing",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
        )

        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, tenant_id)

        logger.debug(
            "Link user tenant request listing validation passed",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
        )

    async def validate_invite_user_to_tenant(self, tenant_id: UUID, authenticated_user_id: UUID, requested_user_id: UUID):
        logger.debug(
            "Validating tenant invite",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
            requested_user_id=requested_user_id,
        )

        # needs to be a tenant admin to invite users to the tenant
        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, tenant_id)

        logger.debug(
            "Authenticated user is tenant admin",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
        )

        user = await self.users_query.get_by_id(requested_user_id)

        # requested user must exist
        if not user:
            logger.debug(
                "Tenant invite validation failed: requested user not found",
                tenant_id=tenant_id,
                requested_user_id=requested_user_id,
            )
            raise NotFoundError("User does not exist!")

        # requested user cannot be already a member of the tenant
        is_requested_user_member = await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, requested_user_id, tenant_id)

        logger.debug(
            "Requested user tenant membership checked",
            tenant_id=tenant_id,
            requested_user_id=requested_user_id,
            is_requested_user_member=is_requested_user_member,
        )

        if is_requested_user_member:
            logger.debug(
                "Tenant invite validation failed: requested user is already tenant member",
                tenant_id=tenant_id,
                requested_user_id=requested_user_id,
            )
            raise ValidationError("This user cannot be invited to the tenant!")

        await self._validate_no_pending_request(tenant_id, requested_user_id)

        logger.debug(
            "Tenant invite validation passed",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
            requested_user_id=requested_user_id,
        )

    async def validate_request_tenant_entry(self, tenant_id: UUID, authenticated_user_id: UUID):
        logger.debug(
            "Validating tenant entry request",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
        )

        # user cannot request tenant entry if they are already a member of the tenant
        is_logged_user_member = await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, authenticated_user_id, tenant_id)

        logger.debug(
            "Authenticated user tenant membership checked",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
            is_logged_user_member=is_logged_user_member,
        )

        if is_logged_user_member:
            logger.debug(
                "Tenant entry request validation failed: authenticated user is already tenant member",
                tenant_id=tenant_id,
                authenticated_user_id=authenticated_user_id,
            )
            raise ValidationError("You are already a member of this tenant!")

        await self._validate_no_pending_request(tenant_id, authenticated_user_id)

        logger.debug(
            "Tenant entry request validation passed",
            tenant_id=tenant_id,
            authenticated_user_id=authenticated_user_id,
        )

    async def validate_approve_or_reject_link_user_tenant_request(self, link_user_tenant_request_id: UUID, authenticated_user_id: UUID) -> Optional[LinkUserTenantRequest]:
        logger.debug(
            "Validating link user tenant request decision",
            link_user_tenant_request_id=link_user_tenant_request_id,
            authenticated_user_id=authenticated_user_id,
        )

        link = await self.link_user_tenant_request_query.get_by_id(link_user_tenant_request_id)

        if not link:
            logger.debug(
                "Link user tenant request decision validation failed: request not found",
                link_user_tenant_request_id=link_user_tenant_request_id,
                authenticated_user_id=authenticated_user_id,
            )
            raise NotFoundError("Link user tenant request not found!")

        logger.debug(
            "Link user tenant request loaded",
            link_user_tenant_request_id=link_user_tenant_request_id,
            authenticated_user_id=authenticated_user_id,
            request_type=link.type,
            tenant_id=link.fk_tenant_id,
            requested_user_id=link.fk_user_id,
        )

        if link.type == LinkUserTenantRequestType.INVITE:
            if await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, authenticated_user_id, link.fk_tenant_id):
                logger.debug(
                    "Link user tenant request decision validation failed: authenticated user is already tenant member",
                    link_user_tenant_request_id=link_user_tenant_request_id,
                    authenticated_user_id=authenticated_user_id,
                    tenant_id=link.fk_tenant_id,
                )
                raise ConflictError("You are already a member of this tenant!")

            # only the user that was invited can approve the invite
            if link.fk_user_id != authenticated_user_id:
                logger.debug(
                    "Link user tenant request decision validation failed: authenticated user is not the invited user",
                    link_user_tenant_request_id=link_user_tenant_request_id,
                    authenticated_user_id=authenticated_user_id,
                    invited_user_id=link.fk_user_id,
                    tenant_id=link.fk_tenant_id,
                )
                raise ForbiddenError("You cannot approve this tenant invite request!")

        if link.type == LinkUserTenantRequestType.REQUEST_ENTRY:
            logger.debug(
                "Validating tenant admin permission for entry request decision",
                link_user_tenant_request_id=link_user_tenant_request_id,
                authenticated_user_id=authenticated_user_id,
                tenant_id=link.fk_tenant_id,
            )

            # only tenant admins can approve tenant entry requests
            await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, link.fk_tenant_id)

        logger.debug(
            "Link user tenant request decision validation passed",
            link_user_tenant_request_id=link_user_tenant_request_id,
            authenticated_user_id=authenticated_user_id,
            request_type=link.type,
            tenant_id=link.fk_tenant_id,
            requested_user_id=link.fk_user_id,
        )

        return link

    async def _validate_no_pending_request(self, tenant_id: UUID, user_id: UUID) -> None:
        pending_request = await self.link_user_tenant_request_query.find_pending_by_tenant_and_user(tenant_id, user_id)

        if not pending_request:
            return

        logger.debug(
            "Link user tenant request validation failed: pending request already exists",
            tenant_id=tenant_id,
            user_id=user_id,
            link_user_tenant_request_id=pending_request.id,
        )
        raise LinkUserTenantRequestAlreadyPending("There is already a pending tenant request for this user!")
