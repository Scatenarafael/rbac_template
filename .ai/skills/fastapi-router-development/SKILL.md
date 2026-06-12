---
name: fastapi-router-development
description: Use when adding or changing FastAPI routers, schemas, dependency injection, middleware interaction or API contracts in the RBAC project.
---

# FastAPI Router Development

## Required References

Read `.ai/project/api-contracts.md`, `.ai/project/security.md` and `.ai/project/tdd-rules.md`.

## Workflow

1. Write a router/contract test first.
2. Define or update Pydantic schemas.
3. Delegate behavior to a use case.
4. Use `DependenciesFactory` / `UseCaseFactory` consistently.
5. Preserve structured error behavior.
6. Run router and use case tests.

## Test Expectations

- Status code.
- Request validation.
- Response shape.
- Dependency delegation.
- Missing/invalid auth cookie where protected.
- Domain error translation when applicable.

## Do Not

- Put business rules directly in routers.
- Access SQLModel models from routers.
- Bypass use cases for new behavior.
