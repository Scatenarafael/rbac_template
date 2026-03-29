# app/domain/exceptions.py
class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


# Exceções específicas
class AuthError(DomainError): ...


class InvalidCredentials(AuthError): ...


class RefreshNotFound(AuthError): ...


class RefreshReuseDetected(AuthError): ...


class RefreshExpired(AuthError): ...


class RefreshInvalid(AuthError): ...
