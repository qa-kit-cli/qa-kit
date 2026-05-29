---
command: qakit.ci.github-actions
description: GitHub Actions CI optimised for Playwright — sharding, trace upload, Docker (Playwright preset).
---

# /qakit.ci.github-actions

Generate a GitHub Actions workflow optimised for a Playwright test suite.

## Context

**Input:** $ARGUMENTS
*(Optional overrides: "add sharding", "use pnpm", "skip webkit".)*

Read before writing:
- `.qakit/memory/test-policy.md` — browser matrix (P0/P1/P2), coverage threshold
- `playwright.config.ts` — `projects` list for the matrix; `retries` setting

## What to generate

`.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  unit:
    name: Unit tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: unit-coverage
          path: coverage/
          retention-days: 30

  playwright:
    name: E2E — ${{ matrix.project }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        # Match the projects array in playwright.config.ts
        # P0 browsers run on every PR; P1/P2 run only on push to main
        project: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      # Install only the browser needed for this matrix shard
      - run: npx playwright install --with-deps ${{ matrix.project }}

      - name: Run Playwright tests
        run: npx playwright test --project=${{ matrix.project }}
        env:
          CI: true
          BASE_URL: ${{ secrets.STAGING_BASE_URL || 'http://localhost:3000' }}
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.project }}
          path: playwright-report/
          retention-days: 14

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-traces-${{ matrix.project }}
          path: test-results/
          retention-days: 7

  # Optional: shard large suites to reduce wall-clock time
  # Uncomment and adjust shard count if E2E suite takes > 10 minutes
  #
  # playwright-sharded:
  #   name: E2E chromium shard ${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
  #   runs-on: ubuntu-latest
  #   strategy:
  #     fail-fast: false
  #     matrix:
  #       shardIndex: [1, 2, 3, 4]
  #       shardTotal: [4]
  #   steps:
  #     - uses: actions/checkout@v4
  #     - uses: actions/setup-node@v4
  #       with: { node-version: '20', cache: 'npm' }
  #     - run: npm ci
  #     - run: npx playwright install --with-deps chromium
  #     - run: npx playwright test --project=chromium --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}

  coverage-gate:
    name: Coverage gate
    needs: unit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: unit-coverage
          path: coverage/
      - name: Check threshold
        run: |
          THRESHOLD=80  # ← replace with value from test-policy.md
          PCT=$(node -e "const s=require('./coverage/coverage-summary.json'); console.log(s.total.lines.pct)")
          echo "Coverage: ${PCT}% (threshold: ${THRESHOLD}%)"
          node -e "if (${PCT} < ${THRESHOLD}) { process.stderr.write('FAIL\n'); process.exit(1); }"
```

## Required adjustments after generating

1. **Browser matrix** — replace `[chromium, firefox, webkit]` with the P0 browsers from `test-policy.md`. Skip webkit on PRs if budget is tight:
   ```yaml
   # Run webkit only on push to main, not on every PR
   if: github.event_name == 'push' || matrix.project != 'webkit'
   ```

2. **Coverage threshold** — replace `80` with the unit line coverage threshold from `test-policy.md`

3. **Secrets** — add these to GitHub repo Settings → Secrets:
   - `STAGING_BASE_URL` — test environment URL
   - `TEST_USER_EMAIL` / `TEST_USER_PASSWORD` — test account credentials

4. **Sharding** — uncomment the sharded job if the suite takes > 10 minutes

5. **Package manager** — replace `npm ci` with `pnpm install --frozen-lockfile` or `yarn install --frozen-lockfile` if needed

## Output

Save to `.github/workflows/tests.yml`. Update rather than replace if file exists.

After writing: `Generated .github/workflows/tests.yml — set STAGING_BASE_URL, TEST_USER_EMAIL, and TEST_USER_PASSWORD secrets before first run`
