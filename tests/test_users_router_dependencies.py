import asyncio

from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.application.usecases import RegisterUserUseCase
from src.modules.auth.presentation.routers.users_router import create, get_register_user_usecase
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody, RegisterUserResponseBody


def test_get_register_user_usecase_injects_session_into_repository():
    session = object()

    usecase = get_register_user_usecase(session=session)

    assert isinstance(usecase, RegisterUserUseCase)
    assert usecase.user_repository._session is session
    assert usecase.users_query._session is session


def test_register_user_response_body_validates_user_entity_with_email_value_object():
    user = User(
        first_name="John",
        last_name="Doe",
        email=Email("john.doe@email.com"),
        hashed_password="hashed-password",
    )

    response = RegisterUserResponseBody.model_validate(user)

    assert response.model_dump() == {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
    }


def test_create_returns_domain_user_for_fastapi_response_model_validation():
    payload = RegisterUserRequestBody(
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        password="secret123",
        re_password="secret123",
    )

    class FakeRegisterUserUseCase:
        async def execute(self, payload: RegisterUserRequestBody) -> User:
            return User(
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=Email(payload.email),
                hashed_password="hashed-password",
            )

    response = asyncio.run(create(payload=payload, create_usecase=FakeRegisterUserUseCase()))

    assert isinstance(response, User)
    assert response.email.value == "john.doe@email.com"
