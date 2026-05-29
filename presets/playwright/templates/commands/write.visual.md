---
command: qakit.write.visual
description: Write Playwright visual regression tests with toHaveScreenshot (Playwright preset).
---

# /qakit.write.visual

Write visual regression tests using Playwright's built-in `toHaveScreenshot()`.

## Context

**Input:** $ARGUMENTS
*(Page route, component, or feature area to capture.)*

Read before writing:
- `.qakit/memory/test-policy.md` — approved visual tool (defaults to Playwright built-in)
- `playwright.config.ts` — `expect.toHaveScreenshot` threshold config

## playwright.config.ts — screenshot config

Add or confirm these settings exist:
```typescript
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,   // allow up to 1% pixel difference
      threshold: 0.2,            // per-pixel colour distance threshold
      animations: 'disabled',   // freeze CSS animations during capture
    },
  },
});
```

## Test pattern

```typescript
import { test, expect } from '@playwright/test';

test.describe('TC-NNN [Page] visual regression', () => {
  test.beforeEach(async ({ page }) => {
    // Disable animations and transition effects for deterministic screenshots
    await page.addStyleTag({ content: '*, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }' });
  });

  test('TC-NNN desktop 1280px matches baseline', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-desktop.png', {
      mask: [
        page.locator('[data-testid="timestamp"]'),   // dynamic: always mask
        page.locator('.user-avatar'),                // user-specific: always mask
        page.locator('[data-testid="ad-banner"]'),   // external content: always mask
      ],
    });
  });

  test('TC-NNN mobile 375px matches baseline', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      mask: [page.locator('[data-testid="timestamp"]')],
    });
  });

  test('TC-NNN dark mode matches baseline', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-dark.png');
  });

  test('TC-NNN component — isolated render matches baseline', async ({ page }) => {
    // Navigate to a Storybook story URL or an isolated component route
    await page.goto('/storybook-static/iframe.html?id=<story-id>');
    await expect(page.locator('[data-component]').first()).toHaveScreenshot(
      'component-default.png',
    );
  });
});
```

## Masking rules

Always mask elements that change between runs:

| Element type | How to identify | Why mask |
|---|---|---|
| Timestamps / relative time | `[data-testid="timestamp"]`, `.time-ago` | Different every run |
| User avatars | `.avatar`, `img[alt*="avatar"]` | Personalised |
| External ads/iframes | `.ad-slot`, `[data-ad]` | External, variable |
| Random IDs in UI | `[data-id]`, `.order-id` | Non-deterministic |
| Loading spinners | `.spinner` | Timing-dependent |

## Establishing and updating baselines

```bash
# First run — generate baseline PNG files
npx playwright test --update-snapshots tests/e2e/visual/

# Update specific test baseline
npx playwright test --update-snapshots -g "TC-NNN desktop"
```

Baseline files live in `tests/e2e/visual/__screenshots__/`. Commit them to source control. Every PR that intentionally changes UI must update baselines and get visual sign-off in review.

## CI integration

Visual tests should run in a Docker container to guarantee consistent font rendering:
```yaml
- name: Run visual tests
  run: npx playwright test tests/e2e/visual/ --project=chromium
  env:
    CI: true
# Baselines generated in CI must use the same Docker image as the comparison run
```

## What to write

For the target in `$ARGUMENTS`:
1. Desktop screenshot (1280×720) with dynamic content masked
2. Mobile screenshot (375×812)
3. Dark mode screenshot (if the app supports it)
4. Error/empty state screenshot (the page in its most visually distinct alternative state)

After writing: `Added N visual tests (TC-NNN through TC-NNN) in <path>`
Include the baseline generation command.
