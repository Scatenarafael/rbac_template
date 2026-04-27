from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from src.core.config.config import get_settings
from src.core.pagination import DEFAULT_PER_PAGE
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase
from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase, DeleteTenantUseCase, ListTenantsUseCase, UpdateTenantUseCase
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.factories import DependenciesFactory
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema

router = APIRouter(tags=["tenants"], prefix="/tenants")
settings = get_settings()


@router.get("/")
async def list_tenants(
    page: Annotated[int | None, Query(ge=1)] = None,
    per_page: Annotated[int, Query(ge=1)] = DEFAULT_PER_PAGE,
    usecase: ListTenantsUseCase = Depends(DependenciesFactory().get_list_tenants_usecase),
):
    if page is None:
        return await usecase.execute()

    return await usecase.execute(page=page, per_page=per_page)


@router.post("/")
async def create_tenant(
    request: Request,
    payload: TenantCreationPayloadSchema,
    usecase: CreateTenantUseCase = Depends(DependenciesFactory().get_create_tenant_usecase),
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

    return await usecase.execute(payload, authenticated_user_id)


@router.put("/{tenant_id}")
async def update_tenant(
    request: Request,
    tenant_id: UUID,
    payload: TenantCreationPayloadSchema,
    usecase: UpdateTenantUseCase = Depends(DependenciesFactory().get_update_tenant_usecase),
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

    return await usecase.execute(tenant_id, payload, authenticated_user_id)


@router.delete("/{tenant_id}")
async def delete_tenant(
    request: Request,
    tenant_id: UUID,
    usecase: DeleteTenantUseCase = Depends(DependenciesFactory().get_delete_tenant_usecase),
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

    return await usecase.execute(tenant_id, authenticated_user_id)
