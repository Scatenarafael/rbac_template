from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.config import get_settings
from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase, MeUseCase, RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.auth_schema import MeResponseBody, SignInRequestPayload

router = APIRouter(tags=["auth"], prefix="/auth")
settings = get_settings()


def get_sign_in_usecase(session: AsyncSession = Depends(get_session)) -> SignInUseCase:
    return AuthUseCaseFactory(session).build_sign_in_usecase()


def get_refresh_token_usecase(session: AsyncSession = Depends(get_session)) -> RefreshTokenUseCase:
    return AuthUseCaseFactory(session).build_refresh_token_usecase()


def get_sign_out_usecase(session: AsyncSession = Depends(get_session)) -> SignOutUseCase:
    return AuthUseCaseFactory(session).build_sign_out_usecase()


def get_me_usecase(session: AsyncSession = Depends(get_session)) -> MeUseCase:
    return AuthUseCaseFactory(session).build_me_usecase()


def get_logged_user_id_usecase(session: AsyncSession = Depends(get_session)) -> GetLoggedUserIdUseCase:
    return AuthUseCaseFactory(session).build_get_logged_userId_usecase()


@router.post("/sign-in")
async def sign_in(response: Response, payload: SignInRequestPayload, sign_in_usecase: SignInUseCase = Depends(get_sign_in_usecase)):
    return await sign_in_usecase.execute(payload=payload, response=response)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, refresh_token_usecase: RefreshTokenUseCase = Depends(get_refresh_token_usecase)):
    return await refresh_token_usecase.execute(request=request, response=response)


@router.post("/sign-out")
async def sign_out(response: Response, sign_out_usecase: SignOutUseCase = Depends(get_sign_out_usecase)):
    await sign_out_usecase.execute(response=response)


@router.get("/me", response_model=MeResponseBody)
async def me(request: Request, me_usecase: MeUseCase = Depends(get_me_usecase), get_user_id_usecase: GetLoggedUserIdUseCase = Depends(get_logged_user_id_usecase)):
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
