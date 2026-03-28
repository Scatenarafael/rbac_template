from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody


class RegisterUserRules:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def validate_user_creation(self, payload: RegisterUserRequestBody):

        if payload.password != payload.re_password:
            raise ValueError("Password confirmation does not match!")

        # Check if the email is already registered
        if await self.user_repository.find_by_email(payload.email):
            raise ValueError("Email not accepted!")
