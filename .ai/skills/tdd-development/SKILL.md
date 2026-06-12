---
name: tdd-development
description: Use for any behavioral change in this RBAC FastAPI project. Enforces Red -> Green -> Refactor before implementing features, bug fixes, use cases, routers, services, repositories, schemas or migrations.
---

# TDD Development

## Required References

Read `.ai/project/tdd-rules.md` and `.ai/project/testing.md` before changing code.

## Workflow

1. Identify the expected behavior and affected layer.
2. Write or update the smallest test that describes the behavior.
3. Confirm the test would fail without the change.
4. Implement the minimum code needed.
5. Run the relevant test command.
6. Refactor only after tests pass.

## Layer Guidance

- Domain: pure unit tests for entities, value objects and exceptions.
- Application: use fakes for repositories, queries and services.
- Presentation: test routers with fake use cases and test middleware separately.
- Infrastructure: test mappers, repositories, queries and transaction behavior.

## Hard Rules

- Do not implement behavior first.
- Do not mix unrelated refactors into Green.
- Do not read or expose `.env` values.
- Do not run migrations unless explicitly requested.
