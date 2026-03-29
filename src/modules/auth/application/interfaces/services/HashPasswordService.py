from abc import ABC, abstractmethod


class IHashPasswordService(ABC):
    @staticmethod
    @abstractmethod
    def hash_password(password: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        pass
