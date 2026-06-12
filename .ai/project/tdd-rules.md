# TDD Rules

This project is TDD-first. Every behavioral change must follow Red -> Green -> Refactor.

## Red

- Understand the expected behavior.
- Create or update the smallest useful test first.
- Prefer behavior-focused tests over internal implementation tests.
- Confirm the test would fail without the implementation by running it when safe or by explicit analysis.

## Green

- Implement the minimum necessary production code.
- Do not refactor broadly during Green.
- Do not add dependencies unless explicitly needed and approved.

## Refactor

- Refactor only with relevant tests passing.
- Preserve public contracts and layer boundaries.
- If coverage is weak, add characterization tests first.

## Mandatory Checklist

- [ ] Expected behavior is clear.
- [ ] A test covers the behavior.
- [ ] The test would fail before implementation.
- [ ] The implementation is minimal.
- [ ] Relevant tests pass.
- [ ] Architecture layers are respected.
- [ ] No secrets are read or exposed.
- [ ] Documentation is updated when relevant.

## Bugs

Bug fixes must begin with a regression test that reproduces the bug.

## Refactors

Refactors must begin by identifying existing tests. If behavior is not covered, add tests before changing production code.

## Migrations

Schema changes must be driven by behavior tests or persistence tests. Do not run migrations automatically without explicit user request.
