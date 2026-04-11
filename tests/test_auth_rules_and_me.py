# pyright: reportArgumentType=false
import asyncio
from uuid import uuid4

import pytest

from src.modules.auth.application.rules.AuthRules import SignInRules
from src.modules.auth.application.usecases.AuthUseCase import MeUseCase
from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.exceptions import InvalidCredentials
from src.modules.auth.domain.value_objects.Emails import Email


class FakeUsersQuery:
    def __init__(self, user=None, me_result=None) -> None:
        self.user = user
        self.me_result = me_result
        self.find_by_email_calls = []
        self.me_calls = []

    async def find_by_email(self, email: str):
        self.find_by_email_calls.append(email)
        return self.user

    async def me(self, user_id):
        self.me_calls.append(user_id)
        return self.me_result


class FakeHashPasswordService:
    def __init__(self, valid: bool) -> None:
        self.valid = valid
        self.verify_calls = []

    def verify_password(self, password: str, hashed_password: str) -> bool:
        self.verify_calls.append((password, hashed_password))
        return self.valid


def make_user() -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email("john.doe@email.com"),
        hashed_password="hashed-password",
    )


def test_sign_in_rules_return_user_when_credentials_are_valid():
    user = make_user()
    users_query = FakeUsersQuery(user=user)
    hash_password_service = FakeHashPasswordService(valid=True)
    rules = SignInRules(users_query, hash_password_service)

    result = asyncio.run(rules.validate("john.doe@email.com", "secret123"))

    assert result is user
    assert users_query.find_by_email_calls == ["john.doe@email.com"]
    assert hash_password_service.verify_calls == [("secret123", "hashed-password")]


def test_sign_in_rules_reject_unknown_user():
    rules = SignInRules(FakeUsersQuery(user=None), FakeHashPasswordService(valid=True))

    with pytest.raises(InvalidCredentials, match="Credentials are not valid"):
        asyncio.run(rules.validate("missing@email.com", "secret123"))


def test_sign_in_rules_reject_invalid_password():
    rules = SignInRules(FakeUsersQuery(user=make_user()), FakeHashPasswordService(valid=False))

    with pytest.raises(InvalidCredentials, match="Credentials are not valid"):
        asyncio.run(rules.validate("john.doe@email.com", "wrong-password"))


def test_me_usecase_returns_user_details_from_query():
    user_id = uuid4()
    me_result = object()
    users_query = FakeUsersQuery(me_result=me_result)
    usecase = MeUseCase(users_query)

    result = asyncio.run(usecase.execute(user_id))

    assert result is me_result
    assert users_query.me_calls == [user_id]


def test_me_usecase_returns_none_when_user_is_missing():
    users_query = FakeUsersQuery(me_result=None)
    usecase = MeUseCase(users_query)

    result = asyncio.run(usecase.execute(uuid4()))

    assert result is None
