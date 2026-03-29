from typing import Generic, TypeVar

from src.core.config.config import get_settings
from src.modules.auth.application.interfaces.services.HandleTokenService import IHandleTokenService
from src.modules.auth.application.interfaces.services.HashPasswordService import IHashPasswordService
from src.modules.auth.application.rules.AuthRules import SignInRules
from src.modules.auth.domain.exceptions import RefreshInvalid
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository
from src.modules.auth.presentation.schemas.pydantic.auth_schema import SignInRequestPayload

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

settings = get_settings()


class SignInUseCase(Generic[TResponse]):
    def __init__(self, user_repository: IUserRepository, hash_password_service: IHashPasswordService, handle_token_service: IHandleTokenService[TResponse]):
        self.user_repository = user_repository
        self.hash_password_service = hash_password_service
        self.handle_token_service = handle_token_service

    async def execute(self, payload: SignInRequestPayload, response: TResponse) -> dict:

        user = await SignInRules(self.user_repository, self.hash_password_service).validate(payload.email, payload.password)

        access_token = await self.handle_token_service.create_access_token(str(user.id))
        refresh_token_data = await self.handle_token_service.create_refresh_token(str(user.id))

        self.handle_token_service.set_access_cookie(response, access_token)
        self.handle_token_service.set_refresh_cookie(response, refresh_token_data["refresh_jti"], refresh_token_data["refresh_token"])

        return {"access_token": access_token, "refresh_token": refresh_token_data["refresh_token"], "refresh_jti": refresh_token_data["refresh_jti"], "user_id": refresh_token_data["user_id"]}


class RefreshTokenUseCase(Generic[TRequest, TResponse]):
    def __init__(self, handle_token_service: IHandleTokenService[TResponse]):
        self.handle_token_service = handle_token_service

    async def execute(self, request: TRequest, response: TResponse) -> dict:

        if not hasattr(request, "cookies"):
            raise ValueError("Request object does not have cookies attribute")

        cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)  # type: ignore

        if not cookie:
            return {"error": "Refresh token not found"}

        # parse cookie (formato jti:raw)
        try:
            jti, raw = cookie.split(":", 1)
        except Exception as exc:
            raise RefreshInvalid("Formato do cookie de refresh invalido") from exc

        refresh_token_data = await self.handle_token_service.rotate_refresh(raw, jti)

        if not refresh_token_data:
            raise ValueError("Invalid refresh token")

        self.handle_token_service.set_access_cookie(response, refresh_token_data["access_token"])
        self.handle_token_service.set_refresh_cookie(response, refresh_token_data["refresh_jti"], refresh_token_data["refresh_token"])

        return {"access_token": refresh_token_data["access_token"]}
