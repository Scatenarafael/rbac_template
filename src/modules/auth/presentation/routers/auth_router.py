from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from src.core.config.config import get_settings
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, MeUseCase, RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.factories import DependenciesFactory
from src.modules.auth.presentation.schemas.pydantic.auth_schema import MeResponseBody, SignInRequestPayload

router = APIRouter(tags=["auth"], prefix="/auth")
settings = get_settings()


@router.post("/sign-in")
async def sign_in(response: Response, payload: SignInRequestPayload, sign_in_usecase: SignInUseCase = Depends(DependenciesFactory().get_sign_in_usecase)):
    return await sign_in_usecase.execute(payload=payload, response=response)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, refresh_token_usecase: RefreshTokenUseCase = Depends(DependenciesFactory().get_refresh_token_usecase)):
    return await refresh_token_usecase.execute(request=request, response=response)


@router.post("/sign-out")
async def sign_out(response: Response, sign_out_usecase: SignOutUseCase = Depends(DependenciesFactory().get_sign_out_usecase)):
    await sign_out_usecase.execute(response=response)


@router.get("/me", response_model=MeResponseBody)
async def me(request: Request, me_usecase: MeUseCase = Depends(DependenciesFactory().get_me_usecase), get_user_id_usecase: GetLoggedUserIdUseCase = Depends(DependenciesFactory().get_logged_user_id_usecase)):
    access_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not access_token:
        raise InvalidCredentials("Access token not found")

    user_id = await get_user_id_usecase.execute(access_token)
    if not user_id:
        raise InvalidCredentials("Access token invalid or expired")

    try:
        authenticated_user_id = UUID(user_id)
    except (TypeError, ValueError) as exc:
        raise InvalidCredentials("Authenticated user identifier is invalid") from exc

    return await me_usecase.execute(user_id=authenticated_user_id)
