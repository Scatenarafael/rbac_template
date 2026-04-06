from src.modules.auth.application.interfaces.services.HashPasswordService import IHashPasswordService
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery


class SignInRules:
    def __init__(self, users_query: IUsersQuery, hash_password_service: IHashPasswordService):
        self.users_query = users_query
        self.hash_password_service = hash_password_service

    async def validate(self, email: str, password: str):
        user = await self.users_query.find_by_email(email)

        if not user:
            raise InvalidCredentials("Credentials are not valid")

        if not self.hash_password_service.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Credentials are not valid")

        return user
