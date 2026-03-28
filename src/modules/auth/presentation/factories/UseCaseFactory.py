from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.services import HashPasswordService
from src.modules.auth.application.usecases.RegisterUserUseCase import RegisterUserUseCase
from src.modules.auth.infrastructure.repositories.Users import UserRepository


class UseCaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def build_register_user_usecase(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(UserRepository(self.session), HashPasswordService())
