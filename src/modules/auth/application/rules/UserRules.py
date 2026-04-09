from uuid import UUID

from src.modules.auth.domain.exceptions import EmailAlreadyExists, ForbiddenError, ValidationError
from src.modules.auth.domain.interfaces.queries.Users import IUsersQuery
from src.modules.auth.presentation.schemas.pydantic.user_schema import PayloadChangePassword, PayloadUpdateUser, RegisterUserRequestBody


class RegisterUserRules:
    def __init__(self, users_query: IUsersQuery):
        self.users_query = users_query

    async def validate_user_creation(self, payload: RegisterUserRequestBody):

        user = await self.users_query.find_by_email(payload.email)

        if user:
            raise EmailAlreadyExists("You cannot use this email!")

        if payload.password != payload.re_password:
            raise ValidationError("Password confirmation does not match!")

        # Check if the email is already registered
        if await self.users_query.find_by_email(payload.email):
            raise EmailAlreadyExists("Email not accepted!")


class UpdateUserRules:
    def __init__(self, users_query: IUsersQuery):
        self.users_query = users_query

    async def validate_user_update(self, payload: PayloadUpdateUser):

        user = None

        if payload.email:
            user = await self.users_query.find_by_email(payload.email)

        if user:
            raise EmailAlreadyExists("You cannot use this email!")

        attrs = [attr if attr == "email" else None for attr in payload]

        if "password" in attrs:
            raise ValidationError("You cannot update the password")


class ChangePasswordRules:
    def __init__(self, users_query: IUsersQuery):
        self.users_query = users_query

    async def validate_password_change(self, payload: PayloadChangePassword, authenticated_user_id: UUID, user_id: UUID):

        if authenticated_user_id != user_id:
            raise ForbiddenError("You can not change this password!")

        if payload.new_password != payload.re_new_password:
            raise ValidationError("Password confirmation does not match!")
