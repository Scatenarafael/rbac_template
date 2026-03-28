# config.py
import os
from functools import lru_cache
from typing import Literal

# from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "rbac"

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    DEBUG: bool = False

    LOG_LEVEL: str = "INFO"

    LOG_JSON: bool = False

    SQL_ECHO: bool = False

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-super-secret")

    ACCESS_SECRET: str = os.getenv("ACCESS_SECRET", "change-me-super-secret")

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    # nomes de cookie
    ACCESS_COOKIE_NAME: str = "access_token"

    REFRESH_COOKIE_NAME: str = "refresh_token"

    # cookie policy (em produção ajuste secure=True e domain)
    COOKIE_SECURE: bool = False  # True em produção (HTTPS)

    COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = "lax"  # 'Lax' ou 'Strict' dependendo do fluxo

    COOKIE_HTTPONLY: bool = True

    COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN")

    DATABASE_URI: str = os.getenv("DATABASE_URI", "sqlite:///./test.db")

    SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:8005/api")

    @field_validator("DEBUG", "LOG_JSON", "SQL_ECHO", mode="before")
    @classmethod
    def parse_bool_flags(cls, value: object) -> bool | object:
        if isinstance(value, bool):
            return value

        if value is None:
            return False

        normalized = str(value).strip().lower()
        truthy_values = {"1", "true", "yes", "on", "debug", "development", "dev"}
        falsy_values = {"0", "false", "no", "off", "release", "production", "prod"}

        if normalized in truthy_values:
            return True

        if normalized in falsy_values:
            return False

        return value


@lru_cache
def get_settings():
    return Settings()
