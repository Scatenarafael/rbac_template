# Testing

## Framework

The project uses pytest. `run_all_tests.py` executes `python -m pytest` from the repository root.

## Current Patterns

- Test files live under `tests/`.
- Names follow `test_*.py`.
- Tests use local fakes heavily.
- Async code is commonly exercised with `asyncio.run(...)`.
- `pytest.raises` is used for domain and validation errors.
- There is at least one `pytest.mark.xfail`, which should be treated as known technical debt.

## Coverage Areas

- Domain value objects and entities.
- Application rules and use cases.
- Routers and dependency factories.
- Auth middleware and logging integration.
- Repositories, mappers and pagination.

## Missing Or Unconfirmed

- No explicit `unit`, `integration`, `e2e` separation.
- No confirmed coverage command.
- No confirmed `pytest-asyncio`.
- No confirmed containerized test database workflow.

## Guidance

- Use fakes for use case tests.
- Test routers with fake use cases when possible.
- Use integration tests when middleware, exception handlers, SQL constraints or migrations matter.
- Prefer behavior names: `test_should_reject_login_when_password_is_invalid` style is acceptable, but match the local `test_*` convention.
