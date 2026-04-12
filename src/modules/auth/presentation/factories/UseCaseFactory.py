from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.rules import TenantRules
from src.modules.auth.application.rules.LinkUserTenantRequestsRules import LinkUserTenantRequestsRules
from src.modules.auth.application.rules.UserRules import ChangePasswordRules, RegisterUserRules, UpdateUserRules
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, MeUseCase, RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.application.usecases.LinkUserTenantRequestUseCase import (
    AproveUserTenantRequestUseCase,
    InviteUserToTenantUseCase,
    ListLinkUserTenantRequestByUserUseCase,
    ListLinkUserTenantRequestUseCase,
    RejectUserTenantRequestUseCase,
    RequestTenantEntryUseCase,
)
from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase, DeleteTenantUseCase, ListTenantsUseCase, UpdateTenantUseCase
from src.modules.auth.application.usecases.UserUseCase import ChangePasswordUseCase, ListUserUseCase, RegisterUserUseCase, UpdateUserUseCase
from src.modules.auth.infrastructure.queries import RefreshTokensQuery, RolesQuery, TenantsQuery, UsersQuery
from src.modules.auth.infrastructure.queries.LinkUserTenantRequests import LinkUserTenantRequestsQuery
from src.modules.auth.infrastructure.queries.UserTenantRoles import UserTenantRolesQuery
from src.modules.auth.infrastructure.repositories import RefreshTokenRepository, TenantsRepository, UserRepository
from src.modules.auth.infrastructure.repositories.LinkUserTenantRequest import LinkUserTenantRequestRepository
from src.modules.auth.infrastructure.repositories.UserTenantRoles import UserTenantRoleRepository
from src.modules.auth.infrastructure.repositories.UserTenants import UserTenantRepository
from src.modules.auth.infrastructure.services import HandleTokenService, HashPasswordService


class UserUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_register_user_usecase(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(UserRepository(self.session), UsersQuery(self.session), HashPasswordService(), RegisterUserRules(UsersQuery(self.session)))

    def build_list_user_usecase(self) -> ListUserUseCase:
        return ListUserUseCase(UsersQuery(self.session))

    def build_update_user_usecase(self) -> UpdateUserUseCase:
        return UpdateUserUseCase(UserRepository(self.session), UsersQuery(self.session), HashPasswordService(), UpdateUserRules(UsersQuery(self.session)))

    def build_change_password_usecase(self) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(UserRepository(self.session), UsersQuery(self.session), HashPasswordService(), ChangePasswordRules(UsersQuery(self.session)))


class LinkUserTenantRequestUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_list_link_user_tenant_request_usecase(self) -> ListLinkUserTenantRequestUseCase:
        return ListLinkUserTenantRequestUseCase(
            LinkUserTenantRequestsQuery(self.session), LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session))
        )

    def build_invite_user_to_tenant_usecase(self) -> InviteUserToTenantUseCase:
        return InviteUserToTenantUseCase(
            LinkUserTenantRequestRepository(self.session), LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session))
        )

    def build_request_tenant_entry_usecase(self) -> RequestTenantEntryUseCase:
        return RequestTenantEntryUseCase(
            LinkUserTenantRequestRepository(self.session), LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session))
        )

    def build_approve_user_tenant_request_usecase(self) -> AproveUserTenantRequestUseCase:
        return AproveUserTenantRequestUseCase(
            LinkUserTenantRequestRepository(self.session),
            UserTenantRepository(self.session),
            UserTenantRoleRepository(self.session),
            RolesQuery(self.session),
            LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session)),
        )

    def build_reject_user_tenant_request_usecase(self) -> RejectUserTenantRequestUseCase:
        return RejectUserTenantRequestUseCase(
            LinkUserTenantRequestRepository(self.session), LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session))
        )

    def build_list_link_user_tenant_request_by_user_usecase(self) -> ListLinkUserTenantRequestByUserUseCase:
        return ListLinkUserTenantRequestByUserUseCase(
            LinkUserTenantRequestsQuery(self.session), LinkUserTenantRequestsRules(UsersQuery(self.session), UserTenantRolesQuery(self.session), LinkUserTenantRequestsQuery(self.session))
        )


class AuthUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_sign_in_usecase(self) -> SignInUseCase:
        return SignInUseCase[Response](
            UsersQuery(self.session),
            HashPasswordService(),
            HandleTokenService(RefreshTokenRepository(self.session), RefreshTokensQuery(self.session)),
        )

    def build_refresh_token_usecase(self) -> RefreshTokenUseCase:
        return RefreshTokenUseCase[Request, Response](HandleTokenService(RefreshTokenRepository(self.session), RefreshTokensQuery(self.session)))

    def build_sign_out_usecase(self) -> SignOutUseCase:
        return SignOutUseCase[Response](HandleTokenService(RefreshTokenRepository(self.session), RefreshTokensQuery(self.session)))

    def build_get_logged_userId_usecase(self) -> GetLoggedUserIdUseCase:
        return GetLoggedUserIdUseCase(HandleTokenService(RefreshTokenRepository(self.session), RefreshTokensQuery(self.session)))

    def build_me_usecase(self) -> MeUseCase:
        return MeUseCase(UsersQuery(self.session))


class TenantUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_create_tenant_usecase(self) -> CreateTenantUseCase:
        return CreateTenantUseCase(
            self.session,
            TenantsRepository(self.session),
            UserTenantRepository(self.session),
            UserTenantRoleRepository(self.session),
            TenantsQuery(self.session),
            UsersQuery(self.session),
            RolesQuery(self.session),
            TenantRules(TenantsQuery(self.session), UsersQuery(self.session), UserTenantRolesQuery(self.session)),
        )

    def build_list_tenants_usecase(self) -> ListTenantsUseCase:
        return ListTenantsUseCase(TenantsQuery(self.session))

    def build_update_tenant_usecase(self) -> UpdateTenantUseCase:
        return UpdateTenantUseCase(
            TenantsRepository(self.session),
            TenantsQuery(self.session),
            TenantRules(TenantsQuery(self.session), UsersQuery(self.session), UserTenantRolesQuery(self.session)),
        )

    def build_delete_tenant_usecase(self) -> DeleteTenantUseCase:
        return DeleteTenantUseCase(
            TenantsRepository(self.session),
            TenantRules(TenantsQuery(self.session), UsersQuery(self.session), UserTenantRolesQuery(self.session)),
        )
