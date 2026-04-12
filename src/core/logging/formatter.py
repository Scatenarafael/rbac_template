from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from src.core.logging.context import get_request_id, get_user_id

RESET_COLOR = "\033[0m"
LOG_LEVEL_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
}


def console_colors_enabled(stream: Any = sys.stdout) -> bool:
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty()) and "NO_COLOR" not in os.environ


def normalize_log_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(key): normalize_log_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [normalize_log_value(item) for item in value]
    return str(value)


class BaseStructuredFormatter(logging.Formatter):
    def build_event(self, record: logging.LogRecord) -> dict[str, Any]:
        event: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        user_id = get_user_id()
        if request_id:
            event["request_id"] = request_id
        if user_id:
            event["user_id"] = user_id

        extra_fields = getattr(record, "extra_fields", {})
        if isinstance(extra_fields, dict):
            for key, value in extra_fields.items():
                if value is not None:
                    event[key] = normalize_log_value(value)

        if record.exc_info:
            exception_type = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            exception_message = str(record.exc_info[1]) if record.exc_info[1] else ""
            event["exception_type"] = exception_type
            event["exception_message"] = exception_message
            event["stacktrace"] = self.formatException(record.exc_info)

        return event


class JsonLogFormatter(BaseStructuredFormatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(self.build_event(record), ensure_ascii=True, default=str)


class ConsoleLogFormatter(BaseStructuredFormatter):
    def __init__(self, use_colors: bool | None = None) -> None:
        super().__init__()
        self.use_colors = console_colors_enabled() if use_colors is None else use_colors

    def format(self, record: logging.LogRecord) -> str:
        event = self.build_event(record)
        timestamp = event.pop("timestamp")
        level = event.pop("level")
        logger = event.pop("logger")
        message = event.pop("message")

        chunks = [
            timestamp,
            f"level={level}",
            f"logger={logger}",
            f"message={json.dumps(message, ensure_ascii=True)}",
        ]

        for key in sorted(event):
            chunks.append(f"{key}={json.dumps(event[key], ensure_ascii=True, default=str)}")

        line = " ".join(chunks)
        color = LOG_LEVEL_COLORS.get(level)

        if not color or not self.use_colors:
            return line

        return f"{color}{line}{RESET_COLOR}"
