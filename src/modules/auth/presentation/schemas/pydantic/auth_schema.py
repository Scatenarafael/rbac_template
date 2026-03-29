from pydantic import BaseModel


class SignInRequestPayload(BaseModel):
    email: str
    password: str
