---
command: qakit.write.pom
description: Generate Page Object Model classes for a set of pages or UI components.
---

# /qakit.write.pom

Generate Page Object Model (POM) classes for the specified pages or user flows.

## Context

**Input:** $ARGUMENTS
*(Provide one or more page names, routes, or component paths. Example: "checkout flow — /cart, /checkout, /confirmation" or "src/pages/Login.tsx".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — POM requirement (required for flows touching ≥ N pages) and approved locator strategy
- `.qakit/memory/test-plan.md` — which journeys use these pages (to name and scope the POM correctly)

If existing POM files are present (e.g., `tests/e2e/pages/`), extend them rather than duplicate.

## Design principles

- One class per page or major component
- Locators as `readonly` properties, never inline strings in action methods
- Action methods return `this` or the next page object (fluent interface) for chaining
- No assertions inside POM classes — assertions belong in the test
- Constructor takes the Playwright `Page` object (or Cypress `cy` context for Cypress POMs)

## Playwright TypeScript POM

```typescript
// tests/e2e/pages/CheckoutPage.ts
import { Page, Locator } from '@playwright/test';

export class CheckoutPage {
  readonly page: Page;

  // Locators — defined once, reused everywhere
  readonly emailInput: Locator;
  readonly cardNumberInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly confirmationHeading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email address');
    this.cardNumberInput = page.getByLabel('Card number');
    this.submitButton = page.getByRole('button', { name: 'Place order' });
    this.errorMessage = page.getByRole('alert');
    this.confirmationHeading = page.getByRole('heading', { name: /order confirmed/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/checkout');
  }

  async fillPaymentDetails(card: { number: string; expiry: string; cvv: string }): Promise<void> {
    await this.cardNumberInput.fill(card.number);
    // …
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async submitAndWaitForConfirmation(): Promise<void> {
    await Promise.all([
      this.page.waitForResponse(resp => resp.url().includes('/api/orders') && resp.status() === 201),
      this.submitButton.click(),
    ]);
  }
}
```

## Cypress POM (if project uses Cypress)

```typescript
// cypress/pages/CheckoutPage.ts
export class CheckoutPage {
  visit(): this {
    cy.visit('/checkout');
    return this;
  }

  fillEmail(email: string): this {
    cy.findByLabelText('Email address').type(email);
    return this;
  }

  submit(): this {
    cy.findByRole('button', { name: 'Place order' }).click();
    return this;
  }
}
```

## What to generate

For each page/component in `$ARGUMENTS`:
1. A POM class file with all visible interactive elements as locator properties
2. Action methods for every distinct user action on that page
3. An index file re-exporting all POMs: `tests/e2e/pages/index.ts`

Also update `tests/e2e/fixtures.ts` (or equivalent) to expose pre-navigated page objects as Playwright fixtures if the project uses fixture composition.

## Output

`tests/e2e/pages/<PageName>.ts` for each page.

After writing, print: `Generated N POM classes in tests/e2e/pages/`
