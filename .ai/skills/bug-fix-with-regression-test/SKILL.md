---
name: bug-fix-with-regression-test
description: Use when fixing a bug. Requires reproducing the defect with a failing regression test before changing production code.
---

# Bug Fix With Regression Test

## Workflow

1. Reproduce or describe the bug.
2. Locate the narrowest behavior boundary that should catch it.
3. Add a regression test that fails for the current behavior.
4. Implement the smallest fix.
5. Run the regression test and relevant nearby tests.
6. Refactor only if protected by tests.

## Where To Put Tests

- Domain bug: `tests/test_domain_value_objects.py` or a focused domain test.
- Rule/use case bug: matching `tests/test_*rules*.py` or `tests/test_*usecase*.py`.
- Router bug: matching `tests/test_*router*.py`.
- Persistence bug: repository/query test, integration if SQL behavior matters.

## Rules

- Do not fix first and add a test afterward.
- The regression test must fail for the original bug.
- Keep the test named for the behavior, not the implementation detail.
