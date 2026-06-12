---
name: sqlmodel-persistence
description: Use when changing SQLModel models, SQLAlchemy repositories, queries, mappers or database persistence behavior in this RBAC project.
---

# SQLModel Persistence

## Required References

Read `.ai/project/architecture.md`, `.ai/project/testing.md` and `.ai/project/security.md`.

## Workflow

1. Start with a repository/query/mapper test.
2. Keep domain entities separate from SQLModel models.
3. Implement mapper changes explicitly.
4. Handle commit, refresh, rollback and integrity errors.
5. Use integration tests when SQL constraints or joins matter.

## Watch Areas

- Unique constraints.
- Cascade deletes.
- AsyncSession transaction boundaries.
- Domain exception translation.
- Pagination queries.

## Do Not

- Leak ORM models into domain behavior.
- Add database behavior without a test.
- Run migrations unless explicitly requested.
