from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.modules.auth.domain.value_objects.Emails import Email


class RegisterUserRequestBody(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    re_password: str


class RegisterUserResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    email: str

    @field_validator("email", mode="before")
    @classmethod
    def unwrap_email(cls, value: str | Email) -> str:
        if isinstance(value, Email):
            return value.value
        return value


class PayloadUpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None
