# Security

## Observed Mechanisms

- JWT access token stored in cookie.
- Opaque refresh token stored in cookie as `jti:raw`.
- Refresh tokens are stored hashed.
- Refresh rotation revokes sessions on reuse or invalid hash.
- `AuthMiddleware` protects non-public paths.
- CORS is configured in `src/core/http/app_factory.py`.
- Domain exceptions are translated into structured HTTP errors.

## Sensitive Configuration Names

- `SECRET_KEY`
- `ACCESS_SECRET`
- `DATABASE_URI`
- Cookie settings and token expiration settings

Never read, copy or expose values from `.env`, `.env.local`, `.env.production`, `.env.development` or similar files.

## TDD Security Rules

- Changes to auth or RBAC require tests for allowed and denied cases.
- Cookie behavior must be tested when token/session code changes.
- Middleware changes must test public paths, protected paths, missing token, invalid token and valid token.
- Role changes must test admin/member/forbidden behavior.
