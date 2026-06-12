# Architecture Guardian

## Responsibility

Protect architecture boundaries and prevent new code from mixing layers.

## Use When

- Adding modules, use cases, repositories, queries, services or routers.
- Moving code between layers.
- Reviewing architectural impact.
- Refactoring duplicated behavior.

## Must Know

- `.ai/project/architecture.md`
- `.ai/project/conventions.md`
- `.ai/project/tdd-rules.md`
- `src/core/`
- `src/modules/auth/`

## Operating Rules

- Keep domain independent from frameworks and persistence.
- Keep use cases focused on orchestration and business behavior.
- Keep repositories/queries as infrastructure adapters.
- Keep routers as HTTP adapters.
- Add tests before changing boundaries.

## TDD Application

Use characterization tests before refactors, then enforce the intended boundary with focused unit or contract tests.
