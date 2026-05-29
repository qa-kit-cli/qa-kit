# /qakit.write.playwright

Write Playwright TypeScript tests for a feature or user journey.

## Description

Generates production-ready Playwright TypeScript test files following the conventions enforced by `test-policy.md`: `page.getByRole`/`getByLabel` locators, `test.describe/step` structure, `expect` auto-retry assertions, `page.route()` for API mocking, and TC-NNN IDs from the test plan.

## Usage

```
/qakit.write.playwright <feature or journey>
```

## Arguments

- Feature name, user journey, or path to the source file/component
- Examples: `"checkout flow — payment step"`, `src/pages/Checkout.tsx`

## Reads from memory

- `.qakit/memory/test-plan.md` — target file paths and TC-NNN IDs for this journey
- `.qakit/memory/test-policy.md` — locator strategy, retry policy, flakiness rules
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases

## Produces

A `*.spec.ts` file at the path specified in `test-plan.md`.

Conventions applied:
- `import { test, expect } from '@playwright/test'`
- `page.getByRole('button', { name: '…' })` — never CSS selectors or XPath
- `test.describe('TC-NNN [journey]', () => { test.step(…) })`
- `await page.waitForResponse(…)` — never `waitForTimeout`

## Example

```
/qakit.write.playwright TC-001 login happy path — src/pages/LoginPage.tsx
```

## Related commands

- `/qakit.write.pom` — generate Page Object Model classes first
- `/qakit.write.fixtures` — generate test fixtures and factories
- `/qakit.write.a11y` — add accessibility assertions to the same page
- `/qakit.maintain.flaky` — fix any tests that become flaky after writing
