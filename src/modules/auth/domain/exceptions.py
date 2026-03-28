# app/domain/exceptions.py
class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass
