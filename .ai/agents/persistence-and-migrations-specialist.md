# Persistence And Migrations Specialist

## Responsibility

Guide SQLModel models, SQLAlchemy repositories/queries and Alembic migrations.

## Use When

- Adding or changing entities, tables, columns, constraints or indexes.
- Changing repositories, queries or mappers.
- Creating migrations.

## Must Know

- `.ai/project/architecture.md`
- `.ai/project/commands.md`
- `.ai/project/testing.md`
- `src/core/infrastructure/database/`
- `src/modules/auth/infrastructure/models/`
- `src/modules/auth/infrastructure/repositories/`
- `src/modules/auth/infrastructure/queries/`
- `src/modules/auth/infrastructure/mappers/`
- `alembic/`

## Operating Rules

- Keep domain entities separate from ORM models.
- Test mappers and repository behavior.
- Test rollback and integrity errors.
- Do not run migrations unless explicitly requested.

## TDD Application

Start with repository/query behavior or schema-dependent test, then change model/migration.
