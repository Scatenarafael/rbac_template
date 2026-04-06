from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.modules.auth.domain.exceptions import EmailAlreadyExists
from src.modules.auth.domain.entities.User import User
from src.modules.auth.domain.interfaces.repositories.Users import IUserRepository
from src.modules.auth.infrastructure.mappers.UserMappers import UserMapper
from src.modules.auth.infrastructure.models.User import UserModel


class UserRepository(IUserRepository):
    async def create(self, data: User) -> User:

        user = UserMapper.from_entity(data)

        self._session.add(user)
        try:
            await self._session.commit()
            await self._session.refresh(user)
        except IntegrityError as exc:
            await self._session.rollback()
            raise EmailAlreadyExists("Email not accepted!") from exc

        return UserMapper.to_entity(user)

    async def update(self, id: UUID, data: dict) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id)  # type: ignore

        result = await self._session.execute(stmt)

        user = result.scalar_one_or_none()

        if user is None:
            return None

        updatable_fields = {
            "first_name": "",
            "last_name": "",
            "email": "",
        }

        updated = False
        for field_name, default_value in updatable_fields.items():
            value = getattr(data, field_name, default_value)

            # Treat entity default values as "not provided" for partial updates.
            if value is None:
                continue
            if value == default_value:
                continue

            if getattr(user, field_name) != value:
                setattr(user, field_name, value)
                updated = True

        if updated:
            try:
                await self._session.commit()
                await self._session.refresh(user)
            except IntegrityError as exc:
                await self._session.rollback()
                raise EmailAlreadyExists("Email not accepted!") from exc

        return UserMapper.to_entity(user)

    async def delete(self, id: UUID) -> None:
        await self._session.execute(delete(UserModel).where(UserModel.id == id))  # type: ignore
        await self._session.commit()
        await self._session.refresh(UserModel)

    async def change_password(self, id: UUID, new_password: str) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        user.hashed_password = new_password  # You should hash the password before storing it
        await self._session.commit()
        await self._session.refresh(user)

        return UserMapper.to_entity(user)
