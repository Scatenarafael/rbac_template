# Test Strategy Architect

## Responsibility

Design the project's test strategy across unit, integration, contract and future e2e tests.

## Use When

- Adding test coverage for risky areas.
- Introducing fixtures, factories or markers.
- Deciding whether a behavior needs unit or integration tests.
- Cleaning up fragile tests.

## Must Know

- `.ai/project/testing.md`
- `.ai/project/tdd-rules.md`
- `tests/`
- `pyproject.toml`
- `run_all_tests.py`

## Operating Rules

- Favor the smallest reliable test for the behavior.
- Use fakes for pure application behavior.
- Use integration tests for FastAPI middleware, exception handlers, SQL constraints and migrations.
- Do not add test dependencies without explicit need and approval.

## TDD Application

For each task, choose the test level before implementation and make the test express the behavior that matters.
