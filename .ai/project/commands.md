# Commands

Only run safe commands unless the user explicitly asks otherwise.

## Test

```bash
python -m pytest
python run_all_tests.py
```

## Development

No official dev script was found. These commands are compatible with the detected stack but require manual validation:

```bash
fastapi dev main.py
uvicorn main:app
```

## Docker

`docker-compose.yml` defines a PostgreSQL service named `db`.

```bash
docker compose up db
```

Do not start containers unless the task requires it.

## Lint / Typecheck

Pylint and Pyright are dev dependencies, but no official command was found.

## Migrations

Alembic is configured, but migration commands must not be run automatically.

```bash
alembic revision --autogenerate -m "<message>"
alembic upgrade head
```

Use only after explicit user approval/request.
