# /qakit.write.a11y

Write automated accessibility tests using axe-core via Playwright.

## Description

Generates accessibility test files that scan pages with `@axe-core/playwright`, check keyboard navigation, test screen-reader-friendly markup (ARIA roles, labels, live regions), and validate colour contrast. Targets WCAG 2.1 AA compliance, as required by `test-policy.md`.

## Usage

```
/qakit.write.a11y <page or component>
```

## Arguments

- Page name, route, or component path to test for accessibility
- Examples: `"login page"`, `"checkout flow"`, `src/components/Modal.tsx`

## Reads from memory

- `.qakit/memory/test-policy.md` — WCAG level required (AA), approved accessibility framework
- `.qakit/memory/test-plan.md` — TC-NNN IDs assigned to accessibility tests

## Produces

`tests/e2e/<page>.a11y.spec.ts` (or appended to an existing spec file).

Checks generated:
- `checkA11y(page)` — runs full axe-core scan; fails on any WCAG 2.1 AA violation
- Tab-order test — verifies focusable elements receive focus in logical order
- Screen reader label test — all form fields have accessible names via `aria-label` or `<label>`
- Keyboard-only interaction — interactive elements reachable and operable without a mouse

```typescript
import { checkA11y, injectAxe } from 'axe-playwright';

test('TC-020 login page has no WCAG 2.1 AA violations', async ({ page }) => {
  await page.goto('/login');
  await injectAxe(page);
  await checkA11y(page, undefined, { runOnly: { type: 'tag', values: ['wcag2aa'] } });
});
```

## Example

```
/qakit.write.a11y login page
```

## Related commands

- `/qakit.review.accessibility` — manual WCAG audit for a component or page
- `/qakit.write.playwright` — add accessibility checks alongside functional tests
