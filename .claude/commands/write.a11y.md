---
command: qakit.write.a11y
description: Write automated accessibility tests using axe-core via Playwright accessibility APIs.
---

# /qakit.write.a11y

Write automated WCAG 2.1 AA accessibility tests for the specified page or component.

## Context

**Input:** $ARGUMENTS
*(Provide the page URL, route, or component path. Example: "/checkout" or "src/components/Modal.tsx".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — whether accessibility tests are required (approved frameworks: axe-core, Playwright)
- `.qakit/memory/test-plan.md` — TC-NNN IDs assigned to the a11y test suite

Check which a11y framework is installed: look for `@axe-core/playwright`, `axe-playwright`, or `cypress-axe` in `package.json`.

## WCAG 2.1 AA — what to check

Tests must cover these four success criterion categories:
- **Perceivable** — alt text on images, captions on video, sufficient colour contrast
- **Operable** — keyboard navigability, no keyboard traps, focus visible, skip links
- **Understandable** — form labels, error messages identify the field, language attribute
- **Robust** — valid HTML, ARIA roles used correctly, name/role/value for custom widgets

## Playwright + axe-core (primary)

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('TC-NNN [Page] accessibility — WCAG 2.1 AA', () => {
  test('TC-NNN has no automatically detectable WCAG 2.1 AA violations', async ({ page }) => {
    await page.goto('/checkout');
    // Wait for dynamic content to fully render before scanning
    await page.waitForLoadState('networkidle');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('TC-NNN all form inputs have accessible labels', async ({ page }) => {
    await page.goto('/checkout');
    const inputs = page.locator('input, select, textarea');
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const type = await input.getAttribute('type');
      if (type === 'hidden') continue;
      // Each visible input must be associated with a label
      const id = await input.getAttribute('id');
      if (id) {
        await expect(page.locator(`label[for="${id}"]`)).toBeVisible();
      } else {
        // aria-label or aria-labelledby must be present
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledBy = await input.getAttribute('aria-labelledby');
        expect(ariaLabel || ariaLabelledBy).toBeTruthy();
      }
    }
  });

  test('TC-NNN entire page is keyboard navigable', async ({ page }) => {
    await page.goto('/checkout');
    // Tab through all interactive elements and confirm none are skipped
    const interactiveLocator = page.locator('a[href], button:not([disabled]), input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])');
    const count = await interactiveLocator.count();
    for (let i = 0; i < count; i++) {
      await page.keyboard.press('Tab');
      const focused = page.locator(':focus');
      await expect(focused).toBeVisible();
    }
  });

  test('TC-NNN error states are announced to screen readers', async ({ page }) => {
    await page.goto('/checkout');
    // Submit empty form to trigger validation errors
    await page.getByRole('button', { name: /submit|place order|continue/i }).click();
    // Error messages must use role="alert" or aria-live
    const alert = page.locator('[role="alert"], [aria-live="polite"], [aria-live="assertive"]');
    await expect(alert.first()).toBeVisible();
  });
});
```

## Cypress + cypress-axe (if project uses Cypress)

```typescript
it('TC-NNN has no WCAG 2.1 AA violations on /checkout', () => {
  cy.visit('/checkout');
  cy.injectAxe();
  cy.checkA11y(undefined, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] },
  });
});
```

## What to write

For the page/component in `$ARGUMENTS`:
1. **Automated axe scan** — full page scan with WCAG 2.1 AA tags
2. **Label coverage test** — every form input has a programmatic label
3. **Keyboard navigation test** — tab order is logical and nothing traps focus
4. **Error announcement test** — validation errors use `role="alert"` or `aria-live`
5. **Focus visibility test** — focused elements have a visible focus ring

If `$ARGUMENTS` is a modal or dialog: additionally test that focus is trapped within the modal while open and returned to the trigger on close.

## Output

`tests/e2e/a11y/<page>.a11y.spec.ts`

After writing, print: `Added N a11y tests (TC-NNN through TC-NNN) in <path>`
