---
name: code-review
description: Use to review changes in this RBAC FastAPI project, prioritizing bugs, missing tests, TDD violations, security risks and architecture boundary regressions.
---

# Code Review

## Required References

Read `.ai/project/architecture.md`, `.ai/project/testing.md`, `.ai/project/security.md` and `.ai/project/conventions.md`.

## Review Order

1. Behavioral bugs.
2. Missing or ineffective tests.
3. TDD violations.
4. Security regressions.
5. Layer boundary violations.
6. Persistence/session risks.
7. Naming and convention drift.

## Output Style

Lead with findings, ordered by severity, with file and line references when available. If no issues are found, say that clearly and mention residual risk or test gaps.

## TDD Questions

- What test failed before the implementation?
- Does the test assert behavior?
- Are bug fixes covered by regression tests?
- Are refactors protected by characterization tests?
