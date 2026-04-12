# pyright: reportArgumentType=false
import asyncio
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from src.modules.auth.domain.entities import LinkUserTenantRequest
from src.modules.auth.domain.exceptions import LinkUserTenantRequestAlreadyPending
from src.modules.auth.infrastructure.repositories.LinkUserTenantRequest import LinkUserTenantRequestRepository


class FakeSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.added = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.refresh_calls = 0

    def add(self, model) -> None:
        self.added.append(model)

    async def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error:
            raise self.commit_error

    async def rollback(self) -> None:
        self.rollback_calls += 1

    async def refresh(self, _model) -> None:
        self.refresh_calls += 1


def duplicate_pending_request_error() -> IntegrityError:
    return IntegrityError(
        "INSERT INTO link_user_tenant_requests ...",
        {},
        Exception('duplicate key value violates unique constraint "uq_link_user_tenant_requests_tenant_user_status"'),
    )


def test_create_translates_pending_request_unique_violation_to_domain_conflict():
    session = FakeSession(commit_error=duplicate_pending_request_error())
    repository = LinkUserTenantRequestRepository(session)
    request = LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())

    with pytest.raises(LinkUserTenantRequestAlreadyPending, match="already a pending tenant request"):
        asyncio.run(repository.create(request))

    assert session.commit_calls == 1
    assert session.rollback_calls == 1
    assert session.refresh_calls == 0


def test_create_reraises_unexpected_integrity_error_after_rollback():
    session = FakeSession(commit_error=IntegrityError("INSERT", {}, Exception("foreign key violation")))
    repository = LinkUserTenantRequestRepository(session)
    request = LinkUserTenantRequest(fk_tenant_id=uuid4(), fk_user_id=uuid4())

    with pytest.raises(IntegrityError, match="foreign key violation"):
        asyncio.run(repository.create(request))

    assert session.commit_calls == 1
    assert session.rollback_calls == 1
    assert session.refresh_calls == 0
