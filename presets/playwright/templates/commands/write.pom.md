---
command: qakit.write.pom
description: Generate Playwright Page Object Models with fixture composition (Playwright preset).
---

# /qakit.write.pom

Generate Page Object Model classes for the specified pages, using Playwright's fixture extension pattern.

## Context

**Input:** $ARGUMENTS
*(Page names, routes, or component paths to build POMs for.)*

Read before writing:
- `.qakit/memory/test-policy.md` — POM requirement threshold and locator strategy
- `playwright.config.ts` — `baseURL` and `testIdAttribute`
- `tests/e2e/fixtures.ts` — extend this file with new POMs; create it if absent

## POM class pattern

```typescript
// tests/e2e/pages/CheckoutPage.ts
import { type Page, type Locator } from '@playwright/test';

export class CheckoutPage {
  readonly page: Page;

  // All locators declared as readonly properties — never inline in methods
  readonly emailInput: Locator;
  readonly cardNumberInput: Locator;
  readonly expiryInput: Locator;
  readonly cvvInput: Locator;
  readonly submitButton: Locator;
  readonly errorAlert: Locator;
  readonly confirmationHeading: Locator;
  readonly orderIdLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput      = page.getByLabel('Email address');
    this.cardNumberInput = page.getByLabel('Card number');
    this.expiryInput     = page.getByLabel('Expiry date');
    this.cvvInput        = page.getByLabel('CVV');
    this.submitButton    = page.getByRole('button', { name: 'Place order' });
    this.errorAlert      = page.getByRole('alert');
    this.confirmationHeading = page.getByRole('heading', { name: /order confirmed/i });
    this.orderIdLink     = page.getByRole('link', { name: /^ord_/ });
  }

  async goto(): Promise<void> {
    await this.page.goto('/checkout');
  }

  async fillCard(card: { number: string; expiry: string; cvv: string }): Promise<void> {
    await this.cardNumberInput.fill(card.number);
    await this.expiryInput.fill(card.expiry);
    await this.cvvInput.fill(card.cvv);
  }

  /** Click submit and wait for the orders API response before returning. */
  async placeOrder(): Promise<void> {
    await Promise.all([
      this.page.waitForResponse(r => r.url().includes('/api/orders') && r.status() === 201),
      this.submitButton.click(),
    ]);
  }

  /** Click submit without waiting — use when testing error paths. */
  async submitForm(): Promise<void> {
    await this.submitButton.click();
  }
}
```

## Fixture extension (required for shared auth state)

Extend Playwright's built-in `test` fixture so every spec that needs a logged-in page gets it automatically:

```typescript
// tests/e2e/fixtures.ts
import { test as base, expect } from '@playwright/test';
import { CheckoutPage } from './pages/CheckoutPage';
import { LoginPage } from './pages/LoginPage';

type AppFixtures = {
  checkoutPage: CheckoutPage;
  loggedInPage: LoginPage;
};

export const test = base.extend<AppFixtures>({
  checkoutPage: async ({ page }, use) => {
    await use(new CheckoutPage(page));
  },

  loggedInPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    // Use storageState if available, otherwise log in fresh
    await loginPage.loginAs({
      email: process.env.TEST_USER_EMAIL ?? 'test@example.com',
      password: process.env.TEST_USER_PASSWORD ?? 'Password1!',
    });
    await use(loginPage);
  },
});

export { expect } from '@playwright/test';
```

Then in tests:
```typescript
import { test, expect } from '../fixtures';  // ← use the extended test

test('TC-NNN checkout with fixture', async ({ checkoutPage }) => {
  await checkoutPage.goto();
  await checkoutPage.fillCard({ number: '4242 4242 4242 4242', expiry: '12/28', cvv: '123' });
  await checkoutPage.placeOrder();
  await expect(checkoutPage.confirmationHeading).toBeVisible();
});
```

## Storage state (auth caching)

For test suites with many authenticated tests, use `storageState` to avoid logging in on every test:

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: './tests/e2e/globalSetup.ts',
  use: {
    storageState: '.auth/user.json',
  },
});

// tests/e2e/globalSetup.ts
import { chromium } from '@playwright/test';

export default async function globalSetup(): Promise<void> {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  // log in once, save storage state
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: '.auth/user.json' });
  await browser.close();
}
```

Add `.auth/` to `.gitignore`.

## What to generate

For each page in `$ARGUMENTS`:
1. A POM class in `tests/e2e/pages/<PageName>.ts`
2. Update `tests/e2e/pages/index.ts` barrel export
3. Update `tests/e2e/fixtures.ts` with the new fixture

After writing: `Generated N POM classes — update TEST_USER_EMAIL/PASSWORD in .env.test`
