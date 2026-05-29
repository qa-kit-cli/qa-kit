---
command: qakit.maintain.upgrade
description: Upgrade a test suite from one framework version to another.
---

# /qakit.maintain.upgrade

Upgrade the test suite to the specified framework version, handling all breaking changes.

## Context

**Input:** $ARGUMENTS
*(Provide the framework and version upgrade. Example: "Playwright 1.40 → 1.50", "Jest 27 → 29", or "Cypress 12 → 13".)*

Before proceeding, read:
- `.qakit/memory/test-policy.md` — approved framework versions (update after upgrading)
- `package.json` — current installed versions

## Step 1 — Identify the current version and target

```bash
# Current installed version
npx playwright --version
npx jest --version
npx cypress --version
```

State: current version = X, target version = Y.

## Step 2 — Read the migration guide

For the frameworks below, the key breaking changes by major version are:

### Playwright major version upgrades

**Check `CHANGELOG.md` at `github.com/microsoft/playwright/releases`**

Common breaking changes:
- `page.waitForNavigation()` deprecated → use `page.waitForURL()` or `Promise.all` with `waitForResponse`
- `frame.waitForFunction()` signature changes
- Locator API introduced in v1.14 — replace `page.$()` and `page.$$()` calls
- `test.use()` for viewport/locale configuration
- `testInfo.outputDir` moved to `testInfo.outputPath()`
- `devices` import moved: `import { devices } from '@playwright/test'`

### Jest major version upgrades

**v27 → v28:**
- Fake timers: `jest.useFakeTimers('legacy')` removed → use `jest.useFakeTimers()`
- `jest-circus` is now the default test runner (was `jest-jasmine2`)
- `--passWithNoTests` default changed

**v28 → v29:**
- `jest.config.js` → `jest.config.ts` support improved
- Snapshot serializer changes
- `--testTimeout` CLI flag renamed

### Cypress major version upgrades

**v12 → v13:**
- `cy.session()` API changes
- Component testing: `mount` import path changed to `cypress/react18` or `cypress/vue`
- `experimentalSessionAndOrigin` removed (now default)

## Step 3 — Update package.json

```bash
npm install --save-dev playwright@latest
# or
npm install --save-dev jest@29
npm install --save-dev @jest/globals@29 babel-jest@29 jest-environment-jsdom@29
```

Run `npm install` and resolve any peer dependency conflicts.

## Step 4 — Run codemod (if available)

```bash
# Playwright codemod
npx playwright codegen --target=typescript --save-storage=auth.json

# Jest upgrade codemod
npx jscodeshift -t node_modules/jest-codemods/dist/transformers/jest-jasmine-globals.js tests/

# Cypress migration tool
npx @cypress/codemod
```

## Step 5 — Fix remaining breaking changes

Scan all test files for the deprecated patterns listed in Step 2 and apply fixes:

```typescript
// Playwright: replace waitForNavigation
// Before
await Promise.all([page.waitForNavigation(), page.click('a')]);

// After
await page.click('a');
await page.waitForURL('**/target-page');
```

```typescript
// Jest: replace jasmine2 globals
// Before
jasmine.createSpy('myMethod')

// After
jest.fn()
```

## Step 6 — Run the full suite

```bash
npx playwright test
npm test
```

Fix any remaining failures introduced by the upgrade. Do not suppress failures with `.skip()` — fix them.

## Step 7 — Update test-policy.md

Update the Approved Frameworks section of `.qakit/memory/test-policy.md` with the new version.

## Output

After completing the upgrade:
1. Updated `package.json` (show diff)
2. List of files changed and what was updated
3. Updated `.qakit/memory/test-policy.md` framework version
4. Final test run result: N tests passed, 0 failed
