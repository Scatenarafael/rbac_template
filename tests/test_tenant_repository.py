# pyright: reportArgumentType=false
import asyncio
from typing import Any, cast
from uuid import uuid4

import pytest

from src.modules.auth.infrastructure.models.LinkUserTenantRequest import LinkUserTenantRequestModel
from src.modules.auth.infrastructure.models.UserTenant import UserTenantModel
from src.modules.auth.infrastructure.models.UserTenantRole import UserTenantRoleModel
from src.modules.auth.infrastructure.repositories.Tenants import TenantsRepository


class FakeSession:
    def __init__(self, fail_on_execute_call: int | None = None) -> None:
        self.fail_on_execute_call = fail_on_execute_call
        self.executed_statements = []
        self.commit_calls = 0
        self.rollback_calls = 0

    async def execute(self, statement):
        self.executed_statements.append(statement)

        if self.fail_on_execute_call == len(self.executed_statements):
            raise RuntimeError("database exploded")

        return None

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1


def test_delete_tenant_relies_on_database_cascade_and_deletes_only_tenant():
    session = FakeSession()
    repository = TenantsRepository(session)

    asyncio.run(repository.delete(uuid4()))

    assert [statement.table.name for statement in session.executed_statements] == ["tenants"]
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_delete_tenant_rolls_back_when_dependency_cleanup_fails():
    session = FakeSession(fail_on_execute_call=1)
    repository = TenantsRepository(session)

    with pytest.raises(RuntimeError, match="database exploded"):
        asyncio.run(repository.delete(uuid4()))

    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_tenant_related_foreign_keys_use_database_delete_cascade():
    user_tenant_tenant_fk = next(iter(cast(Any, UserTenantModel).__table__.c.fk_tenant_id.foreign_keys))
    user_tenant_role_fk = next(iter(cast(Any, UserTenantRoleModel).__table__.c.fk_user_tenant_id.foreign_keys))
    link_request_tenant_fk = next(iter(cast(Any, LinkUserTenantRequestModel).__table__.c.fk_tenant_id.foreign_keys))

    assert user_tenant_tenant_fk.ondelete == "CASCADE"
    assert user_tenant_role_fk.ondelete == "CASCADE"
    assert link_request_tenant_fk.ondelete == "CASCADE"
