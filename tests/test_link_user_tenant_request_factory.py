# pyright: reportArgumentType=false
import pytest

from src.modules.auth.application.usecases.LinkUserTenantRequestUseCase import (
    AproveUserTenantRequestUseCase,
    InviteUserToTenantUseCase,
    ListLinkUserTenantRequestUseCase,
    RejectUserTenantRequestUseCase,
    RequestTenantEntryUseCase,
)
from src.modules.auth.presentation.factories.UseCaseFactory import LinkUserTenantRequestUseCaseFactory


def test_link_user_tenant_request_factory_builds_list_usecase_with_same_session():
    session = object()
    usecase = LinkUserTenantRequestUseCaseFactory(session).build_list_link_user_tenant_request_usecase()

    assert isinstance(usecase, ListLinkUserTenantRequestUseCase)
    assert usecase.link_user_tenant_request_query._session is session
    assert usecase.rules.users_query._session is session
    assert usecase.rules.user_tenant_role_query._session is session
    assert usecase.rules.link_user_tenant_request_query._session is session


def test_link_user_tenant_request_factory_builds_invite_usecase_with_same_session():
    session = object()
    usecase = LinkUserTenantRequestUseCaseFactory(session).build_invite_user_to_tenant_usecase()

    assert isinstance(usecase, InviteUserToTenantUseCase)
    assert usecase.link_user_tenant_request_repository._session is session
    assert usecase.rules.users_query._session is session
    assert usecase.rules.user_tenant_role_query._session is session
    assert usecase.rules.link_user_tenant_request_query._session is session


def test_link_user_tenant_request_factory_builds_request_entry_usecase_with_same_session():
    session = object()
    usecase = LinkUserTenantRequestUseCaseFactory(session).build_request_tenant_entry_usecase()

    assert isinstance(usecase, RequestTenantEntryUseCase)
    assert usecase.link_user_tenant_request_repository._session is session
    assert usecase.rules.users_query._session is session
    assert usecase.rules.user_tenant_role_query._session is session
    assert usecase.rules.link_user_tenant_request_query._session is session


@pytest.mark.xfail(
    raises=TypeError,
    reason="O factory atual não passa user_tenant_repository, user_tenant_role_repository e role_query para o use case de aprovação.",
    strict=True,
)
def test_link_user_tenant_request_factory_builds_approve_usecase_with_same_session():
    session = object()
    usecase = LinkUserTenantRequestUseCaseFactory(session).build_approve_user_tenant_request_usecase()

    assert isinstance(usecase, AproveUserTenantRequestUseCase)
    assert usecase.link_user_tenant_request_repository._session is session
    assert usecase.user_tenant_repository._session is session
    assert usecase.user_tenant_role_repository._session is session
    assert usecase.role_query._session is session
    assert usecase.rules.users_query._session is session
    assert usecase.rules.user_tenant_role_query._session is session
    assert usecase.rules.link_user_tenant_request_query._session is session


def test_link_user_tenant_request_factory_builds_reject_usecase_with_same_session():
    session = object()
    usecase = LinkUserTenantRequestUseCaseFactory(session).build_reject_user_tenant_request_usecase()

    assert isinstance(usecase, RejectUserTenantRequestUseCase)
    assert usecase.link_user_tenant_request_repository._session is session
    assert usecase.rules.users_query._session is session
    assert usecase.rules.user_tenant_role_query._session is session
    assert usecase.rules.link_user_tenant_request_query._session is session
