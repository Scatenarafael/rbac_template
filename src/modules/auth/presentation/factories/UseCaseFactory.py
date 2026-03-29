from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.usecases.AuthUseCase import RefreshTokenUseCase, SignInUseCase
from src.modules.auth.application.usecases.UserUseCase import ListUserUseCase, RegisterUserUseCase
from src.modules.auth.infrastructure.repositories.tokens.RefreshToken import RefreshTokenRepository
from src.modules.auth.infrastructure.repositories.Users import UserRepository
from src.modules.auth.infrastructure.services import HandleTokenService, HashPasswordService


class UserUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_register_user_usecase(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(UserRepository(self.session), HashPasswordService())

    def build_list_user_usecase(self) -> ListUserUseCase:
        return ListUserUseCase(UserRepository(self.session))


class AuthUseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_sign_in_usecase(self) -> SignInUseCase:
        return SignInUseCase[Response](UserRepository(self.session), HashPasswordService(), HandleTokenService(RefreshTokenRepository(self.session)))

    def build_refresh_token_usecase(self) -> RefreshTokenUseCase:
        return RefreshTokenUseCase[Request, Response](HandleTokenService(RefreshTokenRepository(self.session)))
