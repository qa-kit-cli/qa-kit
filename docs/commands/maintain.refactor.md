# /qakit.maintain.refactor

Refactor an existing test file to follow current framework conventions and reduce duplication.

## Description

Reads a test file and applies the conventions in `test-policy.md`: upgrades locators to `getByRole`/`getByLabel`, extracts repeated setup into `beforeEach`, replaces `waitForTimeout` calls, consolidates duplicate fixture creation into shared factories, and ensures TC-NNN IDs are present in all test titles.

Does not change test logic or coverage — only the structure and style.

## Usage

```
/qakit.maintain.refactor <test file>
```

## Arguments

- Path to the test file to refactor
- Examples: `tests/e2e/checkout.spec.ts`, `tests/unit/auth.service.test.ts`

## Reads from memory

- `.qakit/memory/test-policy.md` — current approved conventions (locators, structure, naming)
- `.qakit/memory/test-plan.md` — TC-NNN IDs to add to tests that are missing them

## Produces

The refactored test file, updated in place. Summary of changes printed inline:
- N locators upgraded to `getByRole`/`getByLabel`
- N `waitForTimeout` calls replaced with `waitForResponse`/`waitForSelector`
- N test cases had TC-NNN IDs added
- N duplicated `beforeEach` blocks consolidated

## Example

```
/qakit.maintain.refactor tests/e2e/login.spec.ts
```

## Related commands

- `/qakit.maintain.flaky` — fix flakiness in the same file before refactoring
- `/qakit.maintain.upgrade` — upgrade the test framework version alongside the refactor
