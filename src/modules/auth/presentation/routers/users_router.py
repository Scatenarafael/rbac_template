from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases import RegisterUserUseCase
from src.modules.auth.application.usecases.UserUseCase import ListUserUseCase
from src.modules.auth.presentation.factories.UseCaseFactory import UserUseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody, RegisterUserResponseBody

router = APIRouter(tags=["users"], prefix="/users")


def get_register_user_usecase(session: AsyncSession = Depends(get_session)) -> RegisterUserUseCase:
    return UserUseCaseFactory(session).build_register_user_usecase()


def get_list_user_usecase(session: AsyncSession = Depends(get_session)) -> ListUserUseCase:
    return UserUseCaseFactory(session).build_list_user_usecase()


@router.post("/register", response_model=RegisterUserResponseBody, status_code=status.HTTP_201_CREATED)
async def create(payload: RegisterUserRequestBody, create_usecase: RegisterUserUseCase = Depends(get_register_user_usecase)):
    return await create_usecase.execute(payload=payload)


@router.get("/", response_model=list[RegisterUserResponseBody])
async def list_users(list_usecase: ListUserUseCase = Depends(get_list_user_usecase)):
    return await list_usecase.execute()
