---
name: refactoring-with-safety-tests
description: Use before refactoring this project. Requires identifying or adding safety tests before changing structure, dependencies or architecture boundaries.
---

# Refactoring With Safety Tests

## Workflow

1. Identify the behavior that must remain unchanged.
2. Find existing tests covering that behavior.
3. Add characterization tests if coverage is weak.
4. Refactor in small steps.
5. Run relevant tests after each meaningful step.
6. Avoid changing behavior and structure in the same commit-sized change.

## Common Refactor Targets

- Duplicated token extraction in routers.
- Factory construction complexity.
- Application/presentation coupling.
- Repository/query duplication.

## Guardrails

- Do not move domain toward infrastructure.
- Do not change HTTP contracts during pure refactors.
- Do not alter migrations during unrelated refactors.
