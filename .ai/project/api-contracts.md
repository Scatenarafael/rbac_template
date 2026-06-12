# API Contracts

## Routers

- `src/modules/auth/presentation/routers/auth_router.py`: `/auth`
- `src/modules/auth/presentation/routers/users_router.py`: `/users`
- `src/modules/auth/presentation/routers/tenant_router.py`: `/tenants`
- `src/modules/auth/presentation/routers/link_user_tenant_request_router.py`: `/link-user-tenant-requests`

## Rules

- Routers validate/adapt HTTP input and delegate to use cases.
- Pydantic schemas define request and response contracts.
- Domain errors must be translated by exception handlers.
- Protected routes must validate authenticated user identity.

## TDD Contract Guidance

- New endpoint: write router/contract test first.
- Changed payload: test request validation and response serialization first.
- Changed error: test status, error code, message shape and request id behavior where applicable.
- Changed auth behavior: test missing, invalid and valid token paths first.
