from passlib.context import CryptContext

from src.modules.auth.application.interfaces.services.HashPasswordService import IHashPasswordService

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPasswordService(IHashPasswordService):
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_ctx.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_ctx.verify(plain_password, hashed_password)
