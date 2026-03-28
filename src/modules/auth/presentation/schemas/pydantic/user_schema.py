from typing import Optional

from pydantic import BaseModel


class RegisterUserRequestBody(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    re_password: str


class PayloadUpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None
