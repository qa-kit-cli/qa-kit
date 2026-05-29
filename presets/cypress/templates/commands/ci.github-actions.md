---
command: qakit.ci.github-actions
description: GitHub Actions CI using cypress-io/github-action with Cypress Cloud (Cypress preset).
---

# /qakit.ci.github-actions

Generate a GitHub Actions workflow for a Cypress test suite.

## Context

**Input:** $ARGUMENTS
*(Optional: "add Cypress Cloud", "use pnpm", "add component tests".)*

Read before writing:
- `.qakit/memory/test-policy.md` — coverage threshold, CI gates
- `cypress.config.ts` — `baseUrl`, whether component testing is configured

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

  component:
    name: Cypress component tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          component: true
          build: npm run build
        env:
          CYPRESS_PROJECT_ID: ${{ secrets.CYPRESS_PROJECT_ID }}
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}

  e2e:
    name: Cypress E2E — ${{ matrix.browser }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chrome, firefox, edge]
    steps:
      - uses: actions/checkout@v4

      - name: Start app
        run: npm run build && npx serve -s build -l 3000 &
        # Replace with your actual start command; use wait-on to ensure it's ready

      - uses: cypress-io/github-action@v6
        with:
          browser: ${{ matrix.browser }}
          wait-on: 'http://localhost:3000'
          wait-on-timeout: 60
          # Uncomment to enable Cypress Cloud parallelisation:
          # record: true
          # parallel: true
          # group: 'E2E ${{ matrix.browser }}'
        env:
          CYPRESS_BASE_URL: ${{ secrets.STAGING_BASE_URL || 'http://localhost:3000' }}
          CYPRESS_adminEmail: ${{ secrets.TEST_ADMIN_EMAIL }}
          CYPRESS_adminPassword: ${{ secrets.TEST_ADMIN_PASSWORD }}
          CYPRESS_userEmail: ${{ secrets.TEST_USER_EMAIL }}
          CYPRESS_userPassword: ${{ secrets.TEST_USER_PASSWORD }}
          CYPRESS_PROJECT_ID: ${{ secrets.CYPRESS_PROJECT_ID }}
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots-${{ matrix.browser }}
          path: cypress/screenshots/
          retention-days: 7

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

## Required adjustments

1. **Browser matrix** — adjust `[chrome, firefox, edge]` to match your P0 browsers from `test-policy.md`

2. **App start command** — replace `npm run build && npx serve -s build` with your actual dev/preview server command. Add `wait-on-timeout` if the server takes longer than 60s to start.

3. **Cypress Cloud** (optional but recommended):
   - Set `CYPRESS_PROJECT_ID` and `CYPRESS_RECORD_KEY` in GitHub Secrets
   - Uncomment `record: true` and `parallel: true` for parallelisation across matrix jobs

4. **Component testing** — remove the `component` job if the project doesn't use Cypress component testing

5. **Coverage threshold** — replace `80` with value from `test-policy.md`

6. **Secrets to add** in GitHub Settings → Secrets:
   - `STAGING_BASE_URL`
   - `TEST_USER_EMAIL` / `TEST_USER_PASSWORD`
   - `TEST_ADMIN_EMAIL` / `TEST_ADMIN_PASSWORD`
   - `CYPRESS_PROJECT_ID` / `CYPRESS_RECORD_KEY` (if using Cypress Cloud)

## Output

Save to `.github/workflows/tests.yml`.

After writing: `Generated .github/workflows/tests.yml — set Cypress secrets and update start command before first run`
