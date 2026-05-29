---
command: qakit.write.playwright
description: Write Playwright TypeScript tests for a feature or user journey.
---

# /qakit.write.playwright

Write Playwright TypeScript tests for the specified feature or user journey.

## Context

**Input:** $ARGUMENTS
*(Provide the feature name, user journey, or path to the component/page under test. Example: "checkout flow — payment step" or "src/pages/Checkout.tsx".)*

Before writing, read:
- `.qakit/memory/test-plan.md` — target file paths, TC-NNN IDs assigned to this journey, and the environment matrix
- `.qakit/memory/test-policy.md` — approved locator strategy, flakiness policy, and coverage thresholds
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases for this journey

Also read the source file(s) referenced in `$ARGUMENTS` to understand the actual DOM structure, API calls, and state machine.

## Conventions (mandatory)

Follow these conventions exactly — they are enforced by `test-policy.md`:

**Imports**
```typescript
import { test, expect } from '@playwright/test';
```
Never use the global `page`; always use the fixture parameter.

**Locators** — prefer in this order:
1. `page.getByRole('button', { name: 'Submit' })`
2. `page.getByLabel('Email address')`
3. `page.getByTestId('checkout-submit')` — only when ARIA role/label is absent
4. Never use CSS class selectors or XPath

**Test structure**
```typescript
test.describe('TC-NNN [Journey name]', () => {
  test.beforeEach(async ({ page }) => {
    // navigation and auth setup only
  });

  test('TC-NNN should <expected outcome>', async ({ page }) => {
    await test.step('Arrange — set up preconditions', async () => { … });
    await test.step('Act — perform the user action', async () => { … });
    await test.step('Assert — verify the outcome', async () => { … });
  });
});
```

**Assertions**
- Use `expect(locator).toBeVisible()` not `.isVisible()` — auto-waits and retries
- For network responses: `await page.waitForResponse(url => url.includes('/api/checkout'))`
- Never use `page.waitForTimeout()` — replace with `waitForResponse` or `waitForSelector`

**TC-NNN IDs**
Assign the next available ID from `test-plan.md`. Format: `TC-001`, `TC-002`, …

## What to write

For the journey in `$ARGUMENTS`, write:

1. **Happy path test** — covers the full success scenario end-to-end
2. **Edge case tests** — from the "Edge Cases and Negative Scenarios" section of `qa-strategy.md`
3. **Error state test** — at least one failure path (validation error, network error, or 4xx response)

For each test:
- Use `test.step()` for every distinct action
- Mock external API calls with `page.route()` if the service is not part of the test environment
- Assert both the UI state and (where applicable) the network request payload

## Output

Save tests to the path specified in `test-plan.md` for this journey, e.g.:
`tests/e2e/<feature>/<journey>.spec.ts`

After writing, print a one-line summary:
> Added N tests (TC-NNN through TC-NNN) in `<path>`
