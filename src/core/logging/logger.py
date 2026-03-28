from __future__ import annotations

import logging
from typing import Any

from src.core.logging.context import get_request_id, get_user_id
from src.core.logging.formatter import normalize_log_value
from src.core.logging.ports import LoggerPort


class StructuredLogger(LoggerPort):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(self, msg: str, **fields: Any) -> None:
        self._log(logging.DEBUG, msg, fields)

    def info(self, msg: str, **fields: Any) -> None:
        self._log(logging.INFO, msg, fields)

    def warning(self, msg: str, **fields: Any) -> None:
        self._log(logging.WARNING, msg, fields)

    def error(self, msg: str, **fields: Any) -> None:
        self._log(logging.ERROR, msg, fields)

    def exception(self, msg: str, **fields: Any) -> None:
        self._log(logging.ERROR, msg, fields, exc_info=True)

    def _log(
        self,
        level: int,
        msg: str,
        fields: dict[str, Any],
        exc_info: bool | tuple[type[BaseException], BaseException, Any] | None = None,
    ) -> None:
        extra_fields = {key: normalize_log_value(value) for key, value in fields.items() if value is not None}

        request_id = get_request_id()
        user_id = get_user_id()
        if request_id:
            extra_fields.setdefault("request_id", request_id)
        if user_id:
            extra_fields.setdefault("user_id", user_id)

        self._logger.log(level, msg, extra={"extra_fields": extra_fields}, exc_info=exc_info)


def get_logger(name: str) -> LoggerPort:
    return StructuredLogger(logging.getLogger(name))
