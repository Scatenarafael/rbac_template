import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar, Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .User import UserModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RefreshTokenModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "refresh_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    token_hash: str = Field(sa_column=Column(String(255), nullable=False, unique=True, index=True))

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    expires_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    revoked: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )

    replaced_by: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    fk_user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
        nullable=True,
    )

    user: Optional["UserModel"] = Relationship(back_populates="refresh_tokens")

    def revoke(self, *, replaced_by: str | None = None) -> None:
        self.revoked = True
        self.replaced_by = replaced_by
