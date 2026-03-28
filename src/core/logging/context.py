from __future__ import annotations

import contextvars

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)


def bind_request_id(value: str | None) -> contextvars.Token[str | None]:
    return request_id_var.set(value)


def set_request_id(value: str | None) -> None:
    bind_request_id(value)


def get_request_id() -> str | None:
    return request_id_var.get()


def reset_request_id(token: contextvars.Token[str | None]) -> None:
    request_id_var.reset(token)


def bind_user_id(value: str | None) -> contextvars.Token[str | None]:
    return user_id_var.set(value)


def set_user_id(value: str | None) -> None:
    bind_user_id(value)


def get_user_id() -> str | None:
    return user_id_var.get()


def reset_user_id(token: contextvars.Token[str | None]) -> None:
    user_id_var.reset(token)
