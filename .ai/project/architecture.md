# Architecture

## Stack

Backend Python com FastAPI, Pydantic v2, SQLModel/SQLAlchemy async, Alembic, PostgreSQL, pytest e uv.

## Shape

Arquitetura modular com inspiracao em Clean Architecture, Ports and Adapters e Layered Architecture.

```text
HTTP request
-> FastAPI router / middleware
-> DependenciesFactory / UseCaseFactory
-> application use case
-> application rules
-> domain interfaces
-> infrastructure repository/query/service
-> SQLModel / SQLAlchemy AsyncSession
-> database
```

## Layers

- `src/core`: configuracao, app factory, logging, pagination e database session.
- `src/modules/auth/domain`: entidades, value objects, enums, exceptions e interfaces.
- `src/modules/auth/application`: use cases, rules e interfaces de servicos.
- `src/modules/auth/infrastructure`: SQLModel models, repositories, queries, mappers e services concretos.
- `src/modules/auth/presentation`: routers, middlewares, schemas, DTOs e factories.
- `tests`: pytest suite cobrindo dominio, aplicacao, presentation, infrastructure e core.

## Rules

- Domain must not depend on FastAPI, SQLModel, SQLAlchemy or Pydantic schemas from presentation.
- Use cases should depend on interfaces and services, not direct ORM models.
- Routers should adapt HTTP input/output and delegate business behavior to use cases.
- Repositories and queries are adapters; keep persistence details out of use cases where practical.
- Mappers preserve separation between domain entities and ORM models.
- Any architectural correction must start with characterization tests.
