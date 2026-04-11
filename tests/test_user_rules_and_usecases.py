# pyright: reportArgumentType=false
import asyncio
from uuid import uuid4

import pytest

from src.modules.auth.application.rules.UserRules import ChangePasswordRules, RegisterUserRules, UpdateUserRules
from src.modules.auth.application.usecases.UserUseCase import ChangePasswordUseCase, UpdateUserUseCase
from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.exceptions import EmailAlreadyExists, ForbiddenError, ValidationError
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.presentation.schemas.pydantic.user_schema import PayloadChangePassword, PayloadUpdateUser, RegisterUserRequestBody


class FakeUserRepository:
    def __init__(self) -> None:
        self.update_calls = []
        self.change_password_calls = []

    async def update(self, id, data):
        self.update_calls.append((id, data))
        return make_user(email=data.get("email") or "john.doe@email.com")

    async def change_password(self, id, new_password):
        self.change_password_calls.append((id, new_password))
        return make_user()


class FakeUsersQuery:
    def __init__(self, user=None) -> None:
        self.user = user
        self.find_by_email_calls = []

    async def find_by_email(self, email: str):
        self.find_by_email_calls.append(email)
        return self.user


class FakeHashPasswordService:
    def __init__(self) -> None:
        self.hash_calls = []

    def hash_password(self, password: str) -> str:
        self.hash_calls.append(password)
        return f"hashed::{password}"


class FakeUpdateUserRules:
    def __init__(self) -> None:
        self.calls = []

    async def validate_user_update(self, payload):
        self.calls.append(payload)


class FakeChangePasswordRules:
    def __init__(self) -> None:
        self.calls = []

    async def validate_password_change(self, payload, authenticated_user_id, user_id):
        self.calls.append((payload, authenticated_user_id, user_id))


def make_user(email: str = "john.doe@email.com") -> User:
    return User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email=Email(email),
        hashed_password="hashed-password",
    )


def make_register_payload(password: str = "secret123", re_password: str = "secret123") -> RegisterUserRequestBody:
    return RegisterUserRequestBody(
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        password=password,
        re_password=re_password,
    )


def test_update_user_usecase_validates_and_persists_only_provided_fields():
    user_id = uuid4()
    repository = FakeUserRepository()
    rules = FakeUpdateUserRules()
    usecase = UpdateUserUseCase(repository, FakeUsersQuery(), FakeHashPasswordService(), rules)
    payload = PayloadUpdateUser(first_name="Jane")

    result = asyncio.run(usecase.execute(user_id, payload))

    assert rules.calls == [payload]
    assert repository.update_calls == [(user_id, {"first_name": "Jane"})]
    assert isinstance(result, User)


def test_change_password_usecase_validates_hashes_and_persists_password():
    user_id = uuid4()
    repository = FakeUserRepository()
    hash_password_service = FakeHashPasswordService()
    rules = FakeChangePasswordRules()
    usecase = ChangePasswordUseCase(repository, FakeUsersQuery(), hash_password_service, rules)
    payload = PayloadChangePassword(new_password="new-secret", re_new_password="new-secret")

    asyncio.run(usecase.execute(user_id, payload, authenticated_user_id=user_id, user_id=user_id))

    assert rules.calls == [(payload, user_id, user_id)]
    assert hash_password_service.hash_calls == ["new-secret"]
    assert repository.change_password_calls == [(user_id, "hashed::new-secret")]


def test_register_user_rules_reject_existing_email():
    rules = RegisterUserRules(FakeUsersQuery(user=make_user()))

    with pytest.raises(EmailAlreadyExists, match="You cannot use this email"):
        asyncio.run(rules.validate_user_creation(make_register_payload()))


def test_register_user_rules_reject_password_confirmation_mismatch():
    rules = RegisterUserRules(FakeUsersQuery(user=None))

    with pytest.raises(ValidationError, match="Password confirmation does not match"):
        asyncio.run(rules.validate_user_creation(make_register_payload(password="one", re_password="two")))


def test_update_user_rules_reject_existing_email():
    rules = UpdateUserRules(FakeUsersQuery(user=make_user()))

    with pytest.raises(EmailAlreadyExists, match="You cannot use this email"):
        asyncio.run(rules.validate_user_update(PayloadUpdateUser(email="john.doe@email.com")))


def test_change_password_rules_rejects_password_change_for_another_user():
    rules = ChangePasswordRules(FakeUsersQuery())

    with pytest.raises(ForbiddenError, match="You can not change this password"):
        asyncio.run(
            rules.validate_password_change(
                PayloadChangePassword(new_password="new-secret", re_new_password="new-secret"),
                authenticated_user_id=uuid4(),
                user_id=uuid4(),
            )
        )


def test_change_password_rules_reject_password_confirmation_mismatch():
    user_id = uuid4()
    rules = ChangePasswordRules(FakeUsersQuery())

    with pytest.raises(ValidationError, match="Password confirmation does not match"):
        asyncio.run(
            rules.validate_password_change(
                PayloadChangePassword(new_password="one", re_new_password="two"),
                authenticated_user_id=user_id,
                user_id=user_id,
            )
        )
