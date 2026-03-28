from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases import RegisterUserUseCase
from src.modules.auth.presentation.factories import UseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody

router = APIRouter(tags=["users"], prefix="/users")


def get_register_user_usecase(session: AsyncSession = Depends(get_session)) -> RegisterUserUseCase:
    return UseCaseFactory(session).build_register_user_usecase()


@router.post("/register")
async def create(payload: RegisterUserRequestBody, create_usecase: RegisterUserUseCase = Depends(get_register_user_usecase)):
    try:
        new_user = await create_usecase.execute(payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return new_user
