---
name: auth-and-rbac-security
description: Use when changing authentication, authorization, cookies, JWT access tokens, refresh token rotation, tenant roles or RBAC rules.
---

# Auth And RBAC Security

## Required References

Read `.ai/project/security.md`, `.ai/project/api-contracts.md` and `.ai/project/tdd-rules.md`.

## Workflow

1. Write tests for allowed and denied behavior first.
2. Cover missing credential, invalid credential and forbidden role.
3. Preserve cookie security settings and token contracts.
4. Avoid logging tokens or secrets.
5. Keep auth rules in middleware/rules/use cases, not scattered in routers.

## Critical Files

- `src/modules/auth/presentation/middlewares/auth_middleware.py`
- `src/modules/auth/infrastructure/services/HandleTokenService.py`
- `src/modules/auth/application/rules/`
- `src/modules/auth/presentation/routers/`

## Do Not

- Read `.env` values.
- Print tokens, cookies or secrets.
- Relax protected route behavior without tests.
