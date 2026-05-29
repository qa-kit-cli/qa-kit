---
command: qakit.ci.github-actions
description: Generate a GitHub Actions workflow YAML for the project's test suite.
---

# /qakit.ci.github-actions

Generate a GitHub Actions workflow for the project's test suite and save it to `.github/workflows/tests.yml`.

## Context

**Input:** $ARGUMENTS
*(Optional: override flags like "add Playwright matrix", "include nightly E2E", or "use pnpm". Defaults to inferring from the project.)*

Before writing, read:
- `.qakit/memory/test-policy.md` — environment matrix (browsers, OS), CI/CD gates, coverage threshold
- `.qakit/memory/test-plan.md` — which test types exist and their trigger conditions

Inspect the project to detect:
- Package manager: `package.json` → check for `pnpm-lock.yaml`, `yarn.lock`, or `package-lock.json`
- Test frameworks: check `package.json` `scripts` and `devDependencies`
- Python tests: check for `pyproject.toml` or `pytest.ini`
- Playwright config: `playwright.config.ts` — extract browser list and project names

## What to generate

`.github/workflows/tests.yml` — a complete, production-ready workflow with:

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
          cache: 'npm'             # or pnpm / yarn
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: unit-coverage
          path: coverage/

  integration:
    name: Integration tests
    runs-on: ubuntu-latest
    services:
      postgres:                   # include only if the project uses a DB
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:integration
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb

  e2e:
    name: E2E — ${{ matrix.project }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        project: [chromium, firefox, webkit]   # from playwright.config.ts projects
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps ${{ matrix.project }}
      - run: npx playwright test --project=${{ matrix.project }}
        env:
          CI: true
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.project }}
          path: playwright-report/
          retention-days: 14

  coverage-gate:
    name: Coverage gate
    needs: [unit, integration]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: unit-coverage
          path: coverage/
      - name: Check coverage threshold
        run: |
          COVERAGE=$(node -e "const c=require('./coverage/coverage-summary.json'); console.log(c.total.lines.pct)")
          THRESHOLD=80    # from test-policy.md
          if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
            echo "Coverage $COVERAGE% is below threshold $THRESHOLD%"
            exit 1
          fi
```

## Required adjustments

After generating the YAML:
1. Replace the coverage threshold number with the value from `test-policy.md`
2. Replace the browser matrix with the P0 browsers from `test-policy.md`
3. Add or remove the `services.postgres` block based on whether the project uses a real DB
4. Adjust the package manager (`npm ci` → `pnpm install --frozen-lockfile` or `yarn install --frozen-lockfile`)
5. Add `secrets` references if `playwright.config.ts` reads `process.env` for test account credentials

## Output

Save to `.github/workflows/tests.yml`. If the file already exists, update it rather than replace it — preserve existing job names and step IDs.

After writing, print: `Generated .github/workflows/tests.yml — review the coverage threshold and browser matrix before committing.`
