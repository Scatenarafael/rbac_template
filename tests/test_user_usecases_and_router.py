import asyncio
from uuid import uuid4

from src.modules.auth.application.usecases.UserUseCase import ListUserUseCase, RegisterUserUseCase
from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.routers.users_router import get_list_user_usecase, list_users
from src.modules.auth.presentation.schemas.pydantic.user_schema import RegisterUserRequestBody


class FakeUserRepository:
    def __init__(self, existing_user=None, users=None) -> None:
        self.existing_user = existing_user
        self.users = users or []
        self.created = []
        self.find_by_email_calls = []
        self.list_calls = 0

    async def find_by_email(self, email: str):
        self.find_by_email_calls.append(email)
        return self.existing_user

    async def create(self, user: User) -> User:
        self.created.append(user)
        return user

    async def list(self):
        self.list_calls += 1
        return self.users


class FakeHashPasswordService:
    def __init__(self) -> None:
        self.hash_calls = []

    def hash_password(self, password: str) -> str:
        self.hash_calls.append(password)
        return f"hashed::{password}"


def make_user(email: str = "john.doe@email.com") -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email(email),
        hashed_password="hashed-password",
    )


def test_register_user_usecase_hashes_password_and_persists_email_value_object():
    repository = FakeUserRepository()
    hash_password_service = FakeHashPasswordService()
    usecase = RegisterUserUseCase(repository, hash_password_service)
    payload = RegisterUserRequestBody(
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        password="secret123",
        re_password="secret123",
    )

    user = asyncio.run(usecase.execute(payload))

    assert hash_password_service.hash_calls == ["secret123"]
    assert repository.find_by_email_calls == ["john.doe@email.com"]
    assert repository.created[0].hashed_password == "hashed::secret123"
    assert repository.created[0].email.value == "john.doe@email.com"
    assert user is repository.created[0]


def test_list_user_usecase_returns_repository_result():
    users = [make_user("john@email.com"), make_user("jane@email.com")]
    repository = FakeUserRepository(users=users)
    usecase = ListUserUseCase(repository)

    result = asyncio.run(usecase.execute())

    assert result == users
    assert repository.list_calls == 1


def test_get_list_user_usecase_injects_session_into_repository():
    session = object()

    usecase = get_list_user_usecase(session=session)

    assert isinstance(usecase, ListUserUseCase)
    assert usecase.user_repository._session is session


def test_list_users_returns_usecase_result():
    users = [make_user("john@email.com"), make_user("jane@email.com")]

    class FakeListUserUseCase:
        async def execute(self):
            return users

    result = asyncio.run(list_users(list_usecase=FakeListUserUseCase()))

    assert result == users
