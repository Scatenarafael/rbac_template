from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
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
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory, LinkUserTenantRequestUseCaseFactory, TenantUseCaseFactory, UserUseCaseFactory


class DependenciesFactory:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    def _get_session(self, session: AsyncSession) -> AsyncSession:
        return self.session if self.session is not None else session

    # AuthUseCases

    def get_logged_user_id_usecase(self, session: AsyncSession = Depends(get_session)) -> GetLoggedUserIdUseCase:
        return AuthUseCaseFactory(self._get_session(session)).build_get_logged_userId_usecase()

    def get_sign_in_usecase(self, session: AsyncSession = Depends(get_session)) -> SignInUseCase:
        return AuthUseCaseFactory(self._get_session(session)).build_sign_in_usecase()

    def get_refresh_token_usecase(self, session: AsyncSession = Depends(get_session)) -> RefreshTokenUseCase:
        return AuthUseCaseFactory(self._get_session(session)).build_refresh_token_usecase()

    def get_sign_out_usecase(self, session: AsyncSession = Depends(get_session)) -> SignOutUseCase:
        return AuthUseCaseFactory(self._get_session(session)).build_sign_out_usecase()

    def get_me_usecase(self, session: AsyncSession = Depends(get_session)) -> MeUseCase:
        return AuthUseCaseFactory(self._get_session(session)).build_me_usecase()

    # UserUseCases

    def get_register_user_usecase(self, session: AsyncSession = Depends(get_session)) -> RegisterUserUseCase:
        return UserUseCaseFactory(self._get_session(session)).build_register_user_usecase()

    def get_list_user_usecase(self, session: AsyncSession = Depends(get_session)) -> ListUserUseCase:
        return UserUseCaseFactory(self._get_session(session)).build_list_user_usecase()

    def get_update_user_usecase(self, session: AsyncSession = Depends(get_session)) -> UpdateUserUseCase:
        return UserUseCaseFactory(self._get_session(session)).build_update_user_usecase()

    def get_change_password_usecase(self, session: AsyncSession = Depends(get_session)) -> ChangePasswordUseCase:
        return UserUseCaseFactory(self._get_session(session)).build_change_password_usecase()

    # TenantUseCases

    def get_list_tenants_usecase(self, session: AsyncSession = Depends(get_session)) -> ListTenantsUseCase:
        return TenantUseCaseFactory(self._get_session(session)).build_list_tenants_usecase()

    def get_create_tenant_usecase(self, session: AsyncSession = Depends(get_session)) -> CreateTenantUseCase:
        return TenantUseCaseFactory(self._get_session(session)).build_create_tenant_usecase()

    def get_update_tenant_usecase(self, session: AsyncSession = Depends(get_session)) -> UpdateTenantUseCase:
        return TenantUseCaseFactory(self._get_session(session)).build_update_tenant_usecase()

    def get_delete_tenant_usecase(self, session: AsyncSession = Depends(get_session)) -> DeleteTenantUseCase:
        return TenantUseCaseFactory(self._get_session(session)).build_delete_tenant_usecase()

    # LinkUserTenantRequestUseCases

    def get_list_link_user_tenant_request_usecase(self, session: AsyncSession = Depends(get_session)) -> ListLinkUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_list_link_user_tenant_request_usecase()

    def get_invite_user_to_tenant_usecase(self, session: AsyncSession = Depends(get_session)) -> InviteUserToTenantUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_invite_user_to_tenant_usecase()

    def get_request_tenant_entry_usecase(self, session: AsyncSession = Depends(get_session)) -> RequestTenantEntryUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_request_tenant_entry_usecase()

    def get_approve_user_tenant_request_usecase(self, session: AsyncSession = Depends(get_session)) -> AproveUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_approve_user_tenant_request_usecase()

    def get_reject_user_tenant_request_usecase(self, session: AsyncSession = Depends(get_session)) -> RejectUserTenantRequestUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_reject_user_tenant_request_usecase()

    def get_list_link_user_tenant_request_by_user_usecase(self, session: AsyncSession = Depends(get_session)) -> ListLinkUserTenantRequestByUserUseCase:
        return LinkUserTenantRequestUseCaseFactory(self._get_session(session)).build_list_link_user_tenant_request_by_user_usecase()
