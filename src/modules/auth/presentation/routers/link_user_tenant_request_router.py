from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from src.core.config.config import get_settings
from src.core.pagination import DEFAULT_PER_PAGE
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase
from src.modules.auth.application.usecases.LinkUserTenantRequestUseCase import (
    AproveUserTenantRequestUseCase,
    InviteUserToTenantUseCase,
    ListLinkUserTenantRequestByUserUseCase,
    ListLinkUserTenantRequestUseCase,
    RejectUserTenantRequestUseCase,
    RequestTenantEntryUseCase,
)
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.presentation.factories import DependenciesFactory

router = APIRouter(tags=["link-user-tenant-requests"], prefix="/link-user-tenant-requests")

settings = get_settings()


@router.get("/")
async def list_link_user_tenant_requests_by_user(
    request: Request,
    page: Annotated[int | None, Query(ge=1)] = None,
    per_page: Annotated[int, Query(ge=1)] = DEFAULT_PER_PAGE,
    usecase: ListLinkUserTenantRequestByUserUseCase = Depends(DependenciesFactory().get_list_link_user_tenant_request_by_user_usecase),
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

    if page is None:
        return await usecase.execute(authenticated_user_id)

    return await usecase.execute(authenticated_user_id, page=page, per_page=per_page)


@router.get("/{tenant_id}")
async def list_link_user_tenant_requests_by_tenant_id(
    request: Request,
    tenant_id: UUID,
    page: Annotated[int | None, Query(ge=1)] = None,
    per_page: Annotated[int, Query(ge=1)] = DEFAULT_PER_PAGE,
    usecase: ListLinkUserTenantRequestUseCase = Depends(DependenciesFactory().get_list_link_user_tenant_request_usecase),
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

    if page is None:
        return await usecase.execute(tenant_id, authenticated_user_id)

    return await usecase.execute(tenant_id, authenticated_user_id, page=page, per_page=per_page)


@router.post("/{tenant_id}/invite/{requested_user_id}")
async def invite_user_to_tenant(
    request: Request,
    tenant_id: UUID,
    requested_user_id: UUID,
    usecase: InviteUserToTenantUseCase = Depends(DependenciesFactory().get_invite_user_to_tenant_usecase),
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

    return await usecase.execute(tenant_id, authenticated_user_id, requested_user_id)


@router.post("/{tenant_id}/request-entry")
async def request_tenant_entry(
    request: Request,
    tenant_id: UUID,
    usecase: RequestTenantEntryUseCase = Depends(DependenciesFactory().get_request_tenant_entry_usecase),
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


@router.post("/{link_user_tenant_request_id}/approve")
async def approve_user_tenant_request(
    request: Request,
    link_user_tenant_request_id: UUID,
    usecase: AproveUserTenantRequestUseCase = Depends(DependenciesFactory().get_approve_user_tenant_request_usecase),
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

    return await usecase.execute(link_user_tenant_request_id, authenticated_user_id)


@router.post("/{link_user_tenant_request_id}/reject")
async def reject_user_tenant_request(
    request: Request,
    link_user_tenant_request_id: UUID,
    usecase: RejectUserTenantRequestUseCase = Depends(DependenciesFactory().get_reject_user_tenant_request_usecase),
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

    return await usecase.execute(link_user_tenant_request_id, authenticated_user_id)
