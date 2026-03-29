# src/infrastructure/database/mappers/company_mapper.py
from datetime import datetime
from typing import cast
from uuid import UUID

from src.modules.auth.domain.entities import RefreshToken
from src.modules.auth.infrastructure.models.RefreshToken import RefreshTokenModel


class RefreshTokenMapper:
    @staticmethod
    def to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=UUID(str(model.id)),
            token_hash=str(model.token_hash),
            revoked=bool(model.revoked),
            created_at=cast(datetime, model.created_at),
            expires_at=cast(datetime, model.expires_at),
            replaced_by=cast(str | None, model.replaced_by),
            fk_user_id=cast(UUID | None, model.fk_user_id),
        )

    @staticmethod
    def from_entity(entity: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=entity.id,
            token_hash=entity.token_hash,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            revoked=entity.revoked,
            replaced_by=entity.replaced_by,
            fk_user_id=entity.fk_user_id,
        )
