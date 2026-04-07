from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.rules import TenantRules
from src.modules.auth.application.rules.UserRules import RegisterUserRules
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, MeUseCase, RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase, ListTenantsUseCase, UpdateTenantUseCase
from src.modules.auth.application.usecases.UserUseCase import ListUserUseCase, RegisterUserUseCase
from src.modules.auth.infrastructure.queries import RefreshTokensQuery, RolesQuery, TenantsQuery, UsersQuery
from src.modules.auth.infrastructure.queries.UserTenantRoles import UserTenantRolesQuery
from src.modules.auth.infrastructure.repositories import RefreshTokenRepository, TenantsRepository, UserRepository
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
