from src.modules.auth.application.interfaces.services.HashPasswordService import IHashPasswordService
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository


class SignInRules:
    def __init__(self, user_repository: IUserRepository, hash_password_service: IHashPasswordService):
        self.user_repository = user_repository
        self.hash_password_service = hash_password_service

    async def validate(self, email: str, password: str):
        user = await self.user_repository.find_by_email(email)

        if not user:
            raise InvalidCredentials("Credentials are not valid")

        if not self.hash_password_service.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Credentials are not valid")

        return user
