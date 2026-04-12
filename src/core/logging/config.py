from __future__ import annotations

import logging
import sys

from src.core.config.config import get_settings
from src.core.logging.formatter import ConsoleLogFormatter, JsonLogFormatter, console_colors_enabled


MANAGED_HANDLER_FLAG = "_rbac_managed_handler"


def configure_logging(level: str | None = None, json_logs: bool | None = None) -> None:
    settings = get_settings()
    resolved_level = (level or settings.LOG_LEVEL).upper()
    resolved_json_logs = settings.LOG_JSON if json_logs is None else json_logs

    handler = logging.StreamHandler(sys.stdout)
    formatter = (
        JsonLogFormatter()
        if resolved_json_logs
        else ConsoleLogFormatter(use_colors=console_colors_enabled(handler.stream))
    )
    handler.setLevel(resolved_level)
    handler.setFormatter(formatter)
    setattr(handler, MANAGED_HANDLER_FLAG, True)

    root_logger = logging.getLogger()
    for existing_handler in list(root_logger.handlers):
        if getattr(existing_handler, MANAGED_HANDLER_FLAG, False):
            root_logger.removeHandler(existing_handler)
    root_logger.setLevel(resolved_level)
    root_logger.addHandler(handler)

    logging.captureWarnings(True)

    for logger_name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
    ):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(resolved_level)
        logger.propagate = True
