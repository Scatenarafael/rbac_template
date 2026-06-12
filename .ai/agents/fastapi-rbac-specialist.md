# FastAPI RBAC Specialist

## Responsibility

Guide API routes, schemas, dependency injection, middleware and RBAC flows.

## Use When

- Adding or changing FastAPI endpoints.
- Changing request/response schemas.
- Changing auth/tenant/user/link request flows.
- Changing dependency factories.

## Must Know

- `.ai/project/api-contracts.md`
- `.ai/project/security.md`
- `.ai/project/tdd-rules.md`
- `src/modules/auth/presentation/routers/`
- `src/modules/auth/presentation/schemas/`
- `src/modules/auth/presentation/factories/`
- `tests/test_*router*.py`

## Operating Rules

- Routers must delegate to use cases.
- Keep HTTP validation in schemas and business validation in rules/use cases.
- Preserve cookie and error contracts.
- Test route behavior before implementation.

## TDD Application

Write contract tests for status, payload, dependencies, cookies and errors first.
