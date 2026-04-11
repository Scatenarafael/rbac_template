from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, MeUseCase, RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.application.usecases.LinkUserTenantRequestUseCase import (
    AproveUserTenantRequestUseCase,
    InviteUserToTenantUseCase,
    ListLinkUserTenantRequestUseCase,
    RejectUserTenantRequestUseCase,
    RequestTenantEntryUseCase,
)
from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase, DeleteTenantUseCase, ListTenantsUseCase, UpdateTenantUseCase
from src.modules.auth.application.usecases.UserUseCase import ChangePasswordUseCase, ListUserUseCase, RegisterUserUseCase, UpdateUserUseCase
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory, LinkUserTenantRequestUseCaseFactory, TenantUseCaseFactory, UserUseCaseFactory


class DependenciesFactory:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    # AuthUseCases

    def get_logged_user_id_usecase(self) -> GetLoggedUserIdUseCase:
        return AuthUseCaseFactory(self.session).build_get_logged_userId_usecase()

    def get_sign_in_usecase(self) -> SignInUseCase:
        return AuthUseCaseFactory(self.session).build_sign_in_usecase()

    def get_refresh_token_usecase(self) -> RefreshTokenUseCase:
        return AuthUseCaseFactory(self.session).build_refresh_token_usecase()

    def get_sign_out_usecase(self) -> SignOutUseCase:
        return AuthUseCaseFactory(self.session).build_sign_out_usecase()

    def get_me_usecase(self) -> MeUseCase:
        return AuthUseCaseFactory(self.session).build_me_usecase()

    # UserUseCases

    def get_register_user_usecase(self) -> RegisterUserUseCase:
        return UserUseCaseFactory(self.session).build_register_user_usecase()

    def get_list_user_usecase(self) -> ListUserUseCase:
        return UserUseCaseFactory(self.session).build_list_user_usecase()

    def get_update_user_usecase(self) -> UpdateUserUseCase:
        return UserUseCaseFactory(self.session).build_update_user_usecase()

    def get_change_password_usecase(self) -> ChangePasswordUseCase:
        return UserUseCaseFactory(self.session).build_change_password_usecase()

    # TenantUseCases

    def get_list_tenants_usecase(self) -> ListTenantsUseCase:
        return TenantUseCaseFactory(self.session).build_list_tenants_usecase()

    def get_create_tenant_usecase(self) -> CreateTenantUseCase:
        return TenantUseCaseFactory(self.session).build_create_tenant_usecase()

    def get_update_tenant_usecase(self) -> UpdateTenantUseCase:
        return TenantUseCaseFactory(self.session).build_update_tenant_usecase()

    def get_delete_tenant_usecase(self) -> DeleteTenantUseCase:
        return TenantUseCaseFactory(self.session).build_delete_tenant_usecase()

    # LinkUserTenantRequestUseCases

    def get_list_link_user_tenant_request_usecase(self) -> ListLinkUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self.session).build_list_link_user_tenant_request_usecase()

    def get_invite_user_to_tenant_usecase(self) -> InviteUserToTenantUseCase:
        return LinkUserTenantRequestUseCaseFactory(self.session).build_invite_user_to_tenant_usecase()

    def get_request_tenant_entry_usecase(self) -> RequestTenantEntryUseCase:
        return LinkUserTenantRequestUseCaseFactory(self.session).build_request_tenant_entry_usecase()

    def get_approve_user_tenant_request_usecase(self) -> AproveUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self.session).build_approve_user_tenant_request_usecase()

    def get_reject_user_tenant_request_usecase(self) -> RejectUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self.session).build_reject_user_tenant_request_usecase()
