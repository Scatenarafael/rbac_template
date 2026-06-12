---
name: testing-strategy
description: Use to choose, design or reorganize tests for the RBAC FastAPI project, including unit, integration, router, middleware, repository and future e2e coverage.
---

# Testing Strategy

## Required References

Read `.ai/project/testing.md`, `.ai/project/architecture.md` and `.ai/project/tdd-rules.md`.

## Test Level Selection

- Domain behavior: unit test.
- Use case orchestration: unit test with fakes.
- Router contract: router test with fake use case.
- Middleware/exception/CORS/logging: FastAPI integration-style test.
- Repository/query SQL behavior: repository test; use integration if SQL/constraints matter.
- Migration/schema behavior: integration validation with disposable database when feasible.

## Patterns

- Keep fakes local to tests unless duplication becomes painful.
- Test both success and domain error paths.
- Prefer assertions on public behavior and outputs.
- Avoid tests that only mirror implementation.

## Gaps To Watch

- No confirmed coverage command.
- No explicit unit/integration/e2e markers.
- Async tests currently often use `asyncio.run(...)`.
