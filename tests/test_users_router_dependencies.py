from src.modules.auth.application.usecases import RegisterUserUseCase
from src.modules.auth.presentation.routers.users_router import get_register_user_usecase


def test_get_register_user_usecase_injects_session_into_repository():
    session = object()

    usecase = get_register_user_usecase(session=session)

    assert isinstance(usecase, RegisterUserUseCase)
    assert usecase.user_repository._session is session
