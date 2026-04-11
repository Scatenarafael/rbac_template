from typing import Optional
from uuid import UUID

from src.modules.auth.application.rules.common.utils import CommonRules
from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.enums.LinkUserTenantRequestStatus import LinkUserTenantRequestType
from src.modules.auth.domain.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from src.modules.auth.domain.interfaces.queries.LinkUserTenantRequests import ILinkUserTenantRequestsQuery
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.queries.UserTenantRoles import IUserTenantRoleQuery


class LinkUserTenantRequestsRules:
    def __init__(self, users_query: IUsersQuery, user_tenant_role_query: IUserTenantRoleQuery, link_user_tenant_request_query: ILinkUserTenantRequestsQuery):
        self.users_query = users_query
        self.user_tenant_role_query = user_tenant_role_query
        self.link_user_tenant_request_query = link_user_tenant_request_query

    async def validate_list_link_user_tenant_requests(self, tenant_id: UUID, authenticated_user_id: UUID):
        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, tenant_id)

    async def validate_invite_user_to_tenant(self, tenant_id: UUID, authenticated_user_id: UUID, requested_user_id: UUID):

        # needs to be a tenant admin to invite users to the tenant
        await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, tenant_id)

        user = await self.users_query.get_by_id(requested_user_id)

        # requested user must exist
        if not user:
            raise NotFoundError("User does not exist!")

        # requested user cannot be already a member of the tenant
        is_requested_user_member = await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, requested_user_id, tenant_id)

        if is_requested_user_member:
            raise ValidationError("This user cannot be invited to the tenant!")

    async def validate_request_tenant_entry(self, tenant_id: UUID, authenticated_user_id: UUID):

        # user cannot request tenant entry if they are already a member of the tenant
        is_logged_user_member = await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, authenticated_user_id, tenant_id)

        if is_logged_user_member:
            raise ValidationError("You are already a member of this tenant!")

    async def validate_approve_or_reject_link_user_tenant_request(self, link_user_tenant_request_id: UUID, authenticated_user_id: UUID) -> Optional[LinkUserTenantRequest]:
        link = await self.link_user_tenant_request_query.get_by_id(link_user_tenant_request_id)

        if not link:
            raise NotFoundError("Link user tenant request not found!")

        if link.type == LinkUserTenantRequestType.INVITE:
            if await CommonRules().validates_if_user_is_tenant_member(self.user_tenant_role_query, authenticated_user_id, link.fk_tenant_id):
                raise ConflictError("You are already a member of this tenant!")

            # only the user that was invited can approve the invite
            if link.fk_user_id != authenticated_user_id:
                raise ForbiddenError("You cannot approve this tenant invite request!")

        if link.type == LinkUserTenantRequestType.REQUEST_ENTRY:
            # only tenant admins can approve tenant entry requests
            await CommonRules().validates_if_user_is_tenant_admin(self.user_tenant_role_query, authenticated_user_id, link.fk_tenant_id)

        return link
