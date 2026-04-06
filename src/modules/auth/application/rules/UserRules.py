from src.modules.auth.domain.exceptions import EmailAlreadyExists, ValidationError
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody


class RegisterUserRules:
    def __init__(self, users_query: IUsersQuery):
        self.users_query = users_query

    async def validate_user_creation(self, payload: RegisterUserRequestBody):

        if payload.password != payload.re_password:
            raise ValidationError("Password confirmation does not match!")

        # Check if the email is already registered
        if await self.users_query.find_by_email(payload.email):
            raise EmailAlreadyExists("Email not accepted!")
