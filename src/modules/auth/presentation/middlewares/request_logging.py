from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.core.logging.context import set_request_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        set_request_id(rid)

        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            # Import local evita ciclo (depende do seu layout)

            logger = logging.getLogger("http")

            status = getattr(response, "status_code", 500)
            logger.info(
                "request",
                extra={
                    "fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status,
                        "duration_ms": round(duration_ms, 2),
                    }
                },
            )
