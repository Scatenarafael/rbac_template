import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.core.logging.context import bind_request_id, reset_request_id
from src.core.logging.logger import get_logger

logger = get_logger("src.core.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        request_token = bind_request_id(rid)
        request.state.request_id = rid

        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            status = getattr(response, "status_code", 500)
            logger.info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=status,
                duration_ms=round(duration_ms, 2),
            )
            reset_request_id(request_token)
