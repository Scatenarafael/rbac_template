from src.modules.auth.application.interfaces.services import IHashPasswordService
from src.modules.auth.application.rules import RegisterUserRules
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody


class RegisterUserUseCase:
    def __init__(self, user_repository: IUserRepository, hash_password_service: IHashPasswordService):
        self.user_repository = user_repository
        self.hash_password_service = hash_password_service

    async def execute(self, payload: RegisterUserRequestBody):

        await RegisterUserRules(self.user_repository).validate_user_creation(payload)

        hashed_password = self.hash_password_service.hash_password(payload.password)

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=Email(payload.email),
            hashed_password=hashed_password,
        )

        user = await self.user_repository.create(user)

        return user


class ListUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self):
        return await self.user_repository.list()
