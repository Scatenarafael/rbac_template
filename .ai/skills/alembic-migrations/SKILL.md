---
name: alembic-migrations
description: Use when creating, reviewing or planning Alembic migrations for the RBAC project. Requires safe handling of schema changes and no automatic migration execution.
---

# Alembic Migrations

## Required References

Read `.ai/project/commands.md`, `.ai/project/architecture.md` and `.ai/project/testing.md`.

## Workflow

1. Define the behavior or schema requirement.
2. Add a test or validation plan first.
3. Update SQLModel model if needed.
4. Create or review Alembic revision.
5. Verify upgrade/downgrade logic by inspection or explicit requested execution.

## Rules

- Do not run `alembic upgrade`, `downgrade`, seeds or destructive commands without explicit request.
- Do not expose database credentials.
- Validate async-to-sync driver handling in `alembic/env.py` when changing DB config.

## Review Checklist

- Revision id and down revision are correct.
- Upgrade and downgrade are symmetrical where feasible.
- Data migrations are safe and documented.
- Constraints/indexes match model behavior.
