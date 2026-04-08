from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SignInRequestPayload(BaseModel):
    email: str
    password: str


class MeTenantResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class MeRoleResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class MeUserTenantRoleResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant: MeTenantResponseBody
    role: MeRoleResponseBody


class MeResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: str
    user_tenant_roles: list[MeUserTenantRoleResponseBody]
