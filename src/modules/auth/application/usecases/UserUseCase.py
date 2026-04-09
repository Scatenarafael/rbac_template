from uuid import UUID

from src.modules.auth.application.interfaces.services import IHashPasswordService
from src.modules.auth.application.rules import RegisterUserRules
from src.modules.auth.application.rules.UserRules import ChangePasswordRules, UpdateUserRules
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.schemas.pydantic.user_schema import PayloadChangePassword, PayloadUpdateUser, RegisterUserRequestBody


class RegisterUserUseCase:
    def __init__(self, user_repository: IUserRepository, users_query: IUsersQuery, hash_password_service: IHashPasswordService, rules: RegisterUserRules):
        self.user_repository = user_repository
        self.users_query = users_query
        self.hash_password_service = hash_password_service
        self.rules = rules

    async def execute(self, payload: RegisterUserRequestBody):

        await self.rules.validate_user_creation(payload)

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
    def __init__(self, users_query: IUsersQuery):
        self.users_query = users_query

    async def execute(self):
        return await self.users_query.list()


class UpdateUserUseCase:
    def __init__(self, user_repository: IUserRepository, users_query: IUsersQuery, hash_password_service: IHashPasswordService, rules: UpdateUserRules):
        self.user_repository = user_repository
        self.users_query = users_query
        self.hash_password_service = hash_password_service
        self.rules = rules

    async def execute(self, id: UUID, payload: PayloadUpdateUser):

        await self.rules.validate_user_update(payload)

        user = await self.user_repository.update(id, payload.model_dump(exclude_unset=True))

        return user


class ChangePasswordUseCase:
    def __init__(self, user_repository: IUserRepository, users_query: IUsersQuery, hash_password_service: IHashPasswordService, rules: ChangePasswordRules):
        self.user_repository = user_repository
        self.users_query = users_query
        self.hash_password_service = hash_password_service
        self.rules = rules

    async def execute(self, id: UUID, payload: PayloadChangePassword, authenticated_user_id: UUID, user_id: UUID):

        await self.rules.validate_password_change(payload, authenticated_user_id, user_id)

        hashed_password = self.hash_password_service.hash_password(payload.new_password)

        user = await self.user_repository.change_password(id, hashed_password)

        return user
