from pydantic import BaseModel


class TenantCreationPayloadSchema(BaseModel):
    name: str


class TenantUpdatePayloadSchema(BaseModel):
    name: str
