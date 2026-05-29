# /qakit.write.visual

Set up and write visual regression tests using Playwright screenshots.

## Description

Generates Playwright visual regression test files using `expect(page).toHaveScreenshot()`. On first run, captures baseline screenshots. On subsequent runs, diffs against the baseline and fails on unexpected pixel changes above a configurable threshold.

Also supports Percy integration for PR-level visual review (optional, not a CI gate by default).

## Usage

```
/qakit.write.visual <page or component>
```

## Arguments

- Page, route, or component to capture visually
- Examples: `"dashboard"`, `src/components/HeroSection.tsx`, `"/pricing"`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs for visual tests, target paths
- `.qakit/memory/test-policy.md` — whether visual regression is a CI gate or advisory only

## Produces

`tests/e2e/<page>.visual.spec.ts` with snapshot calls.

Example:
```typescript
test('TC-025 dashboard matches visual baseline', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('dashboard.png', { maxDiffPixelRatio: 0.02 });
});
```

Baseline screenshots are stored in `tests/e2e/__screenshots__/`.

## Example

```
/qakit.write.visual pricing page
```

## Related commands

- `/qakit.write.playwright` — functional tests for the same pages
- `/qakit.maintain.upgrade` — update baselines after intentional UI changes
