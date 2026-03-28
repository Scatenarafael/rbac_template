from uuid import UUID

from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.value_objects.Emails import Email
from src.modules.auth.infrastructure.models.User import UserModel


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UUID(str(model.id)),
            first_name=str(model.first_name),
            last_name=str(model.last_name),
            email=Email(str(model.email)),
            hashed_password=str(model.hashed_password),
        )

    @staticmethod
    def from_entity(entity: User) -> UserModel:

        if entity.id is None or entity.first_name is None or entity.last_name is None or entity.email is None:
            raise ValueError("For creating a new user, all fields except id and created_at should be empty or default.")

        return UserModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email.value,
            hashed_password=entity.hashed_password,
        )
