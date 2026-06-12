# Conventions

## Python

- Use existing Python style and typing.
- Many local files use PascalCase filenames, such as `UserUseCase.py` and `TenantRules.py`; follow the folder's existing convention.
- Keep imports aligned with existing modules.

## Architecture

- Domain entities are separate from ORM models.
- Interfaces use `I*` names.
- Repositories and queries live in infrastructure.
- Rules live in application.
- Routers delegate to use cases.
- Mappers translate between ORM models and domain entities.

## Tests

- Place tests in `tests/`.
- Use behavior-focused names.
- Use local fakes when testing use cases.
- Use integration tests only when the behavior crosses framework/database boundaries.

## Documentation

- Do not document secrets.
- Mark uncertain claims with `Nao foi possivel confirmar com os arquivos analisados.` or `Indicio encontrado, mas requer validacao manual.`
