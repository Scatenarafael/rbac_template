from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases.AuthUseCase import RefreshTokenUseCase, SignInUseCase, SignOutUseCase
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.auth_schema import SignInRequestPayload

router = APIRouter(tags=["auth"], prefix="/auth")


def get_sign_in_usecase(session: AsyncSession = Depends(get_session)) -> SignInUseCase:
    return AuthUseCaseFactory(session).build_sign_in_usecase()


def get_refresh_token_usecase(session: AsyncSession = Depends(get_session)) -> RefreshTokenUseCase:
    return AuthUseCaseFactory(session).build_refresh_token_usecase()


def get_sign_out_usecase(session: AsyncSession = Depends(get_session)) -> SignOutUseCase:
    return AuthUseCaseFactory(session).build_sign_out_usecase()


@router.post("/sign-in")
async def sign_in(response: Response, payload: SignInRequestPayload, sign_in_usecase: SignInUseCase = Depends(get_sign_in_usecase)):
    return await sign_in_usecase.execute(payload=payload, response=response)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, refresh_token_usecase: RefreshTokenUseCase = Depends(get_refresh_token_usecase)):
    return await refresh_token_usecase.execute(request=request, response=response)


@router.post("/sign-out")
async def sign_out(response: Response, sign_out_usecase: SignOutUseCase = Depends(get_sign_out_usecase)):
    await sign_out_usecase.execute(response=response)
