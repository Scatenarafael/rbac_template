from sqlalchemy.orm import configure_mappers

import src.modules.auth.infrastructure.models  # noqa: F401


def test_auth_model_mappers_configure_without_errors():
    configure_mappers()
