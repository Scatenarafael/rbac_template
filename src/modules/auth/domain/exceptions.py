# app/domain/exceptions.py
class DomainError(Exception):
    status_code = 400
    code = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    status_code = 422
    code = "validation_error"


class ConflictError(DomainError):
    status_code = 409
    code = "conflict_error"


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"


class ConfigurationError(DomainError):
    status_code = 500
    code = "configuration_error"


class AuthError(DomainError):
    status_code = 401
    code = "auth_error"


class InvalidCredentials(AuthError):
    code = "invalid_credentials"


class RefreshNotFound(AuthError):
    code = "refresh_not_found"


class RefreshReuseDetected(AuthError):
    status_code = 409
    code = "refresh_reuse_detected"


class RefreshExpired(AuthError):
    code = "refresh_expired"


class RefreshInvalid(AuthError):
    code = "refresh_invalid"


class EmailAlreadyExists(ConflictError):
    code = "email_already_exists"


class TenantAlreadyExists(ConflictError):
    code = "tenant_already_exists"


class UserNotFound(NotFoundError):
    code = "user_not_found"
