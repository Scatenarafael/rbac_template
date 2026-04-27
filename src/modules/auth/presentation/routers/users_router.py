from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from src.core.config.config import get_settings
from src.core.pagination import DEFAULT_PER_PAGE
from src.modules.auth.application.usecases import RegisterUserUseCase
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase
from src.modules.auth.application.usecases.UserUseCase import ChangePasswordUseCase, ListUserUseCase, UpdateUserUseCase
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.factories import DependenciesFactory
from src.modules.auth.presentation.schemas.pydantic.pagination_schema import PaginatedResponseBody
from src.modules.auth.presentation.schemas.pydantic.user_schema import PayloadChangePassword, PayloadUpdateUser, RegisterUserRequestBody, RegisterUserResponseBody

router = APIRouter(tags=["users"], prefix="/users")
settings = get_settings()


@router.post("/register", response_model=RegisterUserResponseBody, status_code=status.HTTP_201_CREATED)
async def create(payload: RegisterUserRequestBody, create_usecase: RegisterUserUseCase = Depends(DependenciesFactory().get_register_user_usecase)):
    return await create_usecase.execute(payload=payload)


@router.get("/", response_model=list[RegisterUserResponseBody] | PaginatedResponseBody[RegisterUserResponseBody])
async def list_users(
    page: Annotated[int | None, Query(ge=1)] = None,
    per_page: Annotated[int, Query(ge=1)] = DEFAULT_PER_PAGE,
    list_usecase: ListUserUseCase = Depends(DependenciesFactory().get_list_user_usecase),
):
    if page is None:
        return await list_usecase.execute()

    return await list_usecase.execute(page=page, per_page=per_page)


@router.put("/{id}", response_model=RegisterUserResponseBody)
async def update_user(id: UUID, payload: PayloadUpdateUser, update_usecase: UpdateUserUseCase = Depends(DependenciesFactory().get_update_user_usecase)):
    return await update_usecase.execute(id, payload)


@router.patch("/{id}", response_model=RegisterUserResponseBody)
async def change_password(
    id: UUID,
    request: Request,
    payload: PayloadChangePassword,
    change_password_usecase: ChangePasswordUseCase = Depends(DependenciesFactory().get_change_password_usecase),
    get_user_id_usecase: GetLoggedUserIdUseCase = Depends(DependenciesFactory().get_logged_user_id_usecase),
):

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

    return await change_password_usecase.execute(id, payload, authenticated_user_id, user_id=id)
