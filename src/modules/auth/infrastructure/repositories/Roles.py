from uuid import UUID

from sqlalchemy import select

from src.modules.auth.domain.entities.Role import Role
from src.modules.auth.domain.interfaces.repositories.Roles import IRolesRepository
from src.modules.auth.infrastructure.mappers.RoleMappers import RoleMapper
from src.modules.auth.infrastructure.models.Role import RoleModel


class RolesRepository(IRolesRepository):
    async def create(self, data: Role) -> Role:

        role_model = RoleMapper.from_entity(data)

        self._session.add(role_model)
        await self._session.commit()
        await self._session.refresh(role_model)
        return RoleMapper.to_entity(role_model)

    async def get_by_id(self, id: UUID) -> Role | None:

        stmt = select(RoleModel).where(RoleModel.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if role_model is None:
            return None
        return RoleMapper.to_entity(role_model)

    async def update(self, id: UUID, data: dict) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if role_model is None:
            return None

        updated = False

        if "name" in data:
            name = data["name"]

            # Keep current value when null is sent for mandatory fields.
            if name is not None:
                normalized_name = str(name).strip().lower()
                if normalized_name and role_model.name != normalized_name:
                    role_model.name = normalized_name
                    updated = True

        if "description" in data:
            description = data["description"]
            normalized_description = None if description is None else str(description).strip() or None
            if role_model.description != normalized_description:
                role_model.description = normalized_description
                updated = True

        if updated:
            await self._session.commit()
            await self._session.refresh(role_model)

        return RoleMapper.to_entity(role_model)

    async def delete(self, id: UUID) -> bool:
        stmt = select(RoleModel).where(RoleModel.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if role_model is None:
            return False

        await self._session.delete(role_model)
        await self._session.commit()
        return True
