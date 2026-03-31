from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database.settings.connection import get_session
from src.modules.auth.application.usecases.AuthUseCase import GetLoggedUserIdUseCase
from src.modules.auth.application.usecases.TenantUseCase import CreateTenantUseCase
from src.modules.auth.presentation.factories.UseCaseFactory import AuthUseCaseFactory, TenantUseCaseFactory
from src.modules.auth.presentation.schemas.pydantic.tenant_schema import TenantCreationPayloadSchema

router = APIRouter(tags=["tenants"], prefix="/tenants")


def get_create_tenant_usecase(session: AsyncSession = Depends(get_session)) -> CreateTenantUseCase:
    return TenantUseCaseFactory(session).build_create_tenant_usecase()


def get_logged_user_id_usecase(session: AsyncSession = Depends(get_session)) -> GetLoggedUserIdUseCase:
    return AuthUseCaseFactory(session).build_get_logged_userId_usecase()


@router.post("/")
async def create_tenant(
    request: Request, payload: TenantCreationPayloadSchema, usecase: CreateTenantUseCase = Depends(get_create_tenant_usecase), get_user_id_usecase: GetLoggedUserIdUseCase = Depends(get_logged_user_id_usecase)
):

    cookies = request.cookies.get("access_token")

    user_id = await get_user_id_usecase.execute(str(cookies))

    return await usecase.execute(payload, UUID(user_id))
