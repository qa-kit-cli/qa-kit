---
command: qakit.ci.matrix
description: Design a cross-browser and platform test matrix and emit the CI configuration for it.
---

# /qakit.ci.matrix

Design a cross-browser/platform test matrix and update the CI configuration to run it.

## Context

**Input:** $ARGUMENTS
*(Optional: constraints like "budget = 20 CI minutes", "add Safari on iOS", or "focus on desktop only".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — existing environment matrix and priority tiers (P0/P1/P2)
- `.qakit/memory/qa-strategy.md` — environment requirements section

Detect the CI system: check for `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`.

## Step 1 — Analyse the current matrix

What is already being tested? List browsers/OS combinations and their CI trigger (PR, push, nightly, release).

## Step 2 — Risk-based matrix design

Recommend a matrix structured by test priority:

### P0 — Must pass before any merge (PR gate)
These run on every PR and must be fast (< 5 min):

| Browser | OS | Viewport | Trigger |
|---|---|---|---|
| Chromium (latest) | Ubuntu | 1280×720 | Every PR |
| Mobile Chrome (emulated) | Ubuntu | 375×812 | Every PR |

### P1 — Must pass before main branch deploy
Run on push to main:

| Browser | OS | Viewport | Trigger |
|---|---|---|---|
| Firefox (latest) | Ubuntu | 1280×720 | Push to main |
| WebKit/Safari | macOS | 1280×720 | Push to main |
| Mobile Safari (emulated) | Ubuntu | 375×812 | Push to main |

### P2 — Nightly / pre-release
Run on schedule or before release tags:

| Browser | OS | Viewport | Trigger |
|---|---|---|---|
| Chrome stable | Windows | 1920×1080 | Nightly |
| Edge | Windows | 1280×720 | Nightly |
| IE11 / legacy | Windows | 1280×768 | Pre-release only |

## Step 3 — Time and cost estimate

Estimate matrix runtime based on suite size:
- N E2E tests × avg M seconds per test = raw runtime
- With K parallel workers = wall-clock time per browser
- Total matrix cost = sum across all P0+P1 browsers

If the total PR gate time exceeds 10 minutes, recommend sharding or scope reduction.

## Step 4 — Emit CI configuration

### GitHub Actions matrix

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      # P0 — PR gate
      - browser: chromium
        os: ubuntu-latest
        trigger: pr
      - browser: chromium-mobile
        os: ubuntu-latest
        trigger: pr
      # P1 — push to main
      - browser: firefox
        os: ubuntu-latest
        trigger: main
      - browser: webkit
        os: macos-latest
        trigger: main
```

Add a `if:` condition to skip P1/P2 browsers on PRs:
```yaml
if: github.event_name == 'push' || matrix.trigger == 'pr'
```

### Playwright config matrix

Update `playwright.config.ts` `projects` array to match:
```typescript
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
],
```

## Step 5 — Update test-policy.md

After emitting the CI config, update the Environment Matrix section of `.qakit/memory/test-policy.md` to reflect the agreed matrix.

## Output

1. Updated CI file (`.github/workflows/tests.yml` or `Jenkinsfile`)
2. Updated `playwright.config.ts` `projects` array
3. Updated `.qakit/memory/test-policy.md` Environment Matrix section

After writing, print a summary of the P0/P1/P2 matrix and estimated CI runtime.
