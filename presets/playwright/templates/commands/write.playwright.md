---
command: qakit.write.playwright
description: Write Playwright TypeScript tests (Playwright preset — opinionated conventions).
---

# /qakit.write.playwright

Write Playwright TypeScript tests for the specified feature or user journey.

## Context

**Input:** $ARGUMENTS
*(Feature name, user journey, or path to the source file under test.)*

Read before writing:
- `.qakit/memory/test-plan.md` — TC-NNN ID range for this journey, target file path
- `.qakit/memory/test-policy.md` — locator strategy, coverage thresholds, flakiness policy
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases
- `playwright.config.ts` — `baseURL`, `testIdAttribute`, `use` defaults, and `projects` list

## playwright.config.ts alignment (mandatory)

Check `playwright.config.ts` before writing tests:

```typescript
// Read these values and use them throughout the test:
// config.use.baseURL       → use in page.goto() without hardcoding the host
// config.use.testIdAttribute → default is "data-testid"; use page.getByTestId() accordingly
// config.projects          → each project = a browser config; tests run against all by default
```

If `playwright.config.ts` does not exist, create a minimal one:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

## Conventions (mandatory)

**Imports — always use named imports from `@playwright/test`:**
```typescript
import { test, expect } from '@playwright/test';
// For fixture extension:
import { test, expect } from '../fixtures';
```

**Locators — strict priority:**
1. `page.getByRole('button', { name: 'Place order' })` — ARIA role + accessible name
2. `page.getByLabel('Email address')` — form input label
3. `page.getByText('Order confirmed')` — visible text (stable prose)
4. `page.getByTestId('checkout-submit')` — only when no accessible name exists
5. Never: CSS class selectors, XPath, `:nth-child()`, or `page.$('.foo')`

**Test anatomy — every test uses `test.step()`:**
```typescript
test.describe('[TC-NNN] Checkout — payment step', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/checkout');
  });

  test('TC-NNN completes order with valid Visa card', async ({ page }) => {
    await test.step('Arrange — add product to cart', async () => {
      await page.getByRole('button', { name: 'Add to cart' }).click();
    });
    await test.step('Act — submit payment form', async () => {
      await page.getByLabel('Card number').fill('4242 4242 4242 4242');
      await page.getByLabel('Expiry').fill('12/28');
      await page.getByLabel('CVV').fill('123');
      await page.getByRole('button', { name: 'Place order' }).click();
    });
    await test.step('Assert — confirmation page shown', async () => {
      await expect(page.getByRole('heading', { name: /order confirmed/i })).toBeVisible();
      await expect(page).toHaveURL(/\/orders\/ord_/);
    });
  });
});
```

**Waiting — never use `waitForTimeout`:**
- Network: `await page.waitForResponse(r => r.url().includes('/api/orders') && r.status() === 201)`
- Visibility: `await expect(locator).toBeVisible()` (auto-retries for up to `timeout` ms)
- Navigation: `await page.waitForURL('**/confirmation')`

**Mocking external calls:**
```typescript
await page.route('**/api/payment/charge', route =>
  route.fulfill({ status: 200, json: { id: 'ch_test_123', status: 'succeeded' } })
);
```

**TC-NNN IDs** — assign the next available IDs from `test-plan.md`.

## What to write

1. **Happy path** — full success scenario with a network mock for any external payment/auth service
2. **Validation error path** — form submission with invalid input; assert inline error messages
3. **Network error path** — stub 500 from the API; assert user-visible error state, not a crash
4. **At least one mobile test** — wrap in `test.use({ ...devices['Pixel 5'] })` for the most critical scenario

## Output

Path from `test-plan.md` for this journey, e.g. `tests/e2e/<feature>/<journey>.spec.ts`.

After writing: `Added N tests (TC-NNN through TC-NNN) in <path>`
