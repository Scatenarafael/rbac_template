# app/presentation/middlewares/auth_middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config.config import get_settings
from src.modules.auth.infrastructure.services import HandleTokenService

PUBLIC_PATHS = ["/auth/sign-in", "/auth/refresh", "/auth/sign-out", "/users/register", "/docs", "/openapi.json"]

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # libera rotas públicas
        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # obter access token do cookie
        access_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
        if not access_token:
            return JSONResponse({"detail": "Access token not found"}, status_code=status.HTTP_401_UNAUTHORIZED)

        payload = await HandleTokenService(refresh_token_repository=None).verify_access_token(access_token)
        if not payload:
            # token inválido ou expirado
            return JSONResponse({"detail": "Access token invalid or expired"}, status_code=status.HTTP_401_UNAUTHORIZED)

        # coloca user_id no state para uso nos endpoints
        request.state.user_id = payload.get("sub")
        return await call_next(request)
