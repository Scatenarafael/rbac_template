# Security Reviewer

## Responsibility

Review authentication, authorization, cookies, tokens, secrets and RBAC behavior.

## Use When

- Changing `AuthMiddleware`.
- Changing `HandleTokenService`.
- Changing protected routers.
- Changing role/permission rules.
- Touching settings or environment handling.

## Must Know

- `.ai/project/security.md`
- `.ai/project/api-contracts.md`
- `.ai/project/tdd-rules.md`
- `src/modules/auth/presentation/middlewares/auth_middleware.py`
- `src/modules/auth/infrastructure/services/HandleTokenService.py`
- `src/modules/auth/application/rules/`

## Operating Rules

- Never read or expose `.env` values.
- Test allowed and denied paths.
- Do not log tokens, cookies or secrets.
- Preserve structured error responses.

## TDD Application

Security changes require tests for success, missing credential, invalid credential and forbidden role where applicable.
