---
command: qakit.write.a11y
description: Additional Playwright-specific accessibility test patterns (appended by Playwright preset).
---

## Playwright preset — additional accessibility patterns

The following patterns are specific to `@axe-core/playwright`. Apply them in addition to the base accessibility test suite above.

### Import

```typescript
import AxeBuilder from '@axe-core/playwright';
```

Install if not present: `npm install --save-dev @axe-core/playwright`

### Scoped component scan

Rather than scanning the full page, scan a specific component to isolate violations:

```typescript
test('TC-NNN modal has no WCAG 2.1 AA violations', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Payment help' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();

  const results = await new AxeBuilder({ page })
    .include('[role="dialog"]')          // scan only the modal
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

### Excluding known false-positives

When a third-party widget cannot be fixed, exclude it with a documented reason:

```typescript
const results = await new AxeBuilder({ page })
  .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
  .exclude('#stripe-payment-element')  // third-party iframe — accessibility managed by Stripe
  .analyze();
```

Always add a comment explaining why the exclusion is justified.

### Reporting violations as structured output

When a violation is found, surface the full impact details in the test failure message:

```typescript
if (results.violations.length > 0) {
  const details = results.violations
    .map(v => `[${v.impact}] ${v.id}: ${v.description}\n  ${v.nodes.map(n => n.html).join('\n  ')}`)
    .join('\n\n');
  expect.soft(results.violations, `Accessibility violations:\n${details}`).toHaveLength(0);
}
```

Use `expect.soft()` so all violations are reported in a single test failure rather than stopping at the first one.

### Focus trap testing for modals (Playwright-specific)

```typescript
test('TC-NNN modal traps focus and returns it on close', async ({ page }) => {
  await page.goto('/checkout');
  const triggerButton = page.getByRole('button', { name: 'Open modal' });
  await triggerButton.click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();

  // Tab should stay within the modal
  await page.keyboard.press('Tab');
  const firstFocused = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  await page.keyboard.press('Tab');
  // ... cycle through all focusable elements inside the dialog

  // Escape closes and returns focus to trigger
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(triggerButton).toBeFocused();
});
```
