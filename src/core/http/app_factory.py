from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData

from src.core.config.config import get_settings
from src.core.logging.config import configure_logging
from src.core.logging.http import RequestContextMiddleware, register_exception_handlers
from src.core.logging.logger import get_logger
from src.modules.auth.presentation.middlewares.auth_middleware import AuthMiddleware
from src.modules.auth.presentation.routers import auth_router, link_user_tenant_request_router, tenant_router, users_router

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "http://192.168.15.7:5173",
    "http://192.168.15.6:5173",
    "http://192.168.1.120:4173",
    "http://192.168.1.120:5173",
]

metadata = MetaData()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger = get_logger("src.core.http.lifecycle")
    logger.info(
        "Application startup",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(level=settings.LOG_LEVEL, json_logs=settings.LOG_JSON)

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    # Production checklist validation should run on startup before serving requests.

    # Starlette wraps the last added middleware outermost; CORS must see auth errors and preflights.
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(tenant_router)
    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(link_user_tenant_request_router)

    return app
