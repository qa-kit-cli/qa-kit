---
command: qakit.write.visual
description: Set up and write visual regression tests using Playwright screenshots.
---

# /qakit.write.visual

Write visual regression tests for the specified page or component using Playwright screenshot comparison.

## Context

**Input:** $ARGUMENTS
*(Provide the page, route, or component to capture. Example: "/dashboard" or "src/components/PricingTable.tsx".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — approved visual testing tool (Playwright built-in screenshots or Percy)
- `.qakit/memory/test-plan.md` — TC-NNN IDs for the visual test suite

Check for Percy (`@percy/playwright`) in `package.json`. If present, use Percy. Otherwise use Playwright's built-in `toHaveScreenshot()`.

## Playwright built-in visual regression

```typescript
// playwright.config.ts — ensure this is set
// expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.01 } }

import { test, expect } from '@playwright/test';

test.describe('TC-NNN [Page] visual regression', () => {
  test('TC-NNN desktop layout matches baseline', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    // Mask dynamic content that changes on every run
    await expect(page).toHaveScreenshot('dashboard-desktop.png', {
      mask: [page.locator('[data-testid="timestamp"]'), page.locator('.avatar-image')],
      maxDiffPixelRatio: 0.01,
    });
  });

  test('TC-NNN mobile layout matches baseline', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      mask: [page.locator('[data-testid="timestamp"]')],
    });
  });

  test('TC-NNN component — PricingTable all tiers', async ({ page }) => {
    await page.goto('/storybook-static/iframe.html?id=pricing-table--all-tiers');
    await expect(page.locator('[data-component="PricingTable"]')).toHaveScreenshot(
      'pricing-table-all-tiers.png',
    );
  });

  test('TC-NNN dark mode layout matches baseline', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-dark.png');
  });
});
```

## Percy (if installed)

```typescript
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('TC-NNN dashboard — Percy snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await percySnapshot(page, 'Dashboard — Desktop');
});
```

## Baseline management

**First run (establishing baselines):**
```bash
# Playwright — generates baseline PNG files in tests/e2e/__screenshots__/
npx playwright test --update-snapshots
```
Commit the baseline PNG files to source control. Reviewer must visually approve them in the PR.

**Masking strategy:**
Always mask:
- Timestamps, dates, and relative time strings (`"2 minutes ago"`)
- User avatars and profile pictures
- Any randomly generated content (IDs, nonces)
- External ad or analytics iframes

**Viewport matrix:**
Write tests for at least:
- Desktop: 1280×720
- Tablet: 768×1024
- Mobile: 375×812

## What to write

For the page/component in `$ARGUMENTS`:
1. Full-page screenshot at desktop viewport
2. Full-page screenshot at mobile viewport (375px)
3. Dark mode screenshot (if the app supports it)
4. Component-level screenshot if a Storybook story or isolated render URL exists
5. A state screenshot for each major interactive state (hover, focus, error, loading, empty)

## Output

`tests/e2e/visual/<page>.visual.spec.ts`

After writing, print: `Added N visual tests (TC-NNN through TC-NNN) in <path>`
Include instructions for generating baselines on first run.
