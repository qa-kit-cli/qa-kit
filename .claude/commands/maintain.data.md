---
command: qakit.maintain.data
description: Audit and clean up test data — orphaned fixtures, hardcoded values, environment coupling.
---

# /qakit.maintain.data

Audit the test data setup and clean up problems that cause brittle or environment-coupled tests.

## Context

**Input:** $ARGUMENTS
*(Optional: specific directory or entity type to audit. Example: "tests/fixtures/", "checkout flow data", or "all hardcoded user IDs".)*

Before auditing, read:
- `.qakit/memory/test-plan.md` — Data Model section for the intended fixture strategy
- `.qakit/memory/qa-strategy.md` — Data Requirements section for PII rules
- `.qakit/memory/test-policy.md` — approved fixture approach

Scan:
- `tests/fixtures/`, `cypress/fixtures/`, `tests/factories/`, `tests/seed/` for existing data files
- All test files for inline hardcoded data
- CI environment variable files for data-related secrets

## Step 1 — Inventory all test data

List every data source used by the test suite:

| Type | Path / pattern | Used by | Last modified |
|---|---|---|---|
| JSON fixture | | | |
| Factory function | | | |
| Seed script | | | |
| Hardcoded inline | | | |
| Environment variable | | | |
| External test account | | | |

## Step 2 — Detect hardcoded values

Scan test files for these anti-patterns:

**Hardcoded IDs** — brittle when the DB is reset:
```typescript
// Bad
const user = await db.users.findById('usr_12345'); // breaks when DB is refreshed

// Good
const user = await db.users.findByEmail('test+standard@example.com');
// or: created fresh via factory in beforeEach
```

**Hardcoded credentials:**
```typescript
// Bad
await loginPage.loginAs({ email: 'admin@company.com', password: 'SuperSecret123' }); // real credentials!

// Good
await loginPage.loginAs({ email: process.env.TEST_ADMIN_EMAIL!, password: process.env.TEST_ADMIN_PASSWORD! });
// or: use a factory-created user with a known test password
```

**Environment-coupled URLs:**
```typescript
// Bad
await page.goto('https://staging.myapp.com/checkout'); // environment assumption

// Good
await page.goto(`${process.env.BASE_URL}/checkout`);
// or in playwright.config.ts: baseURL: process.env.BASE_URL
```

**Real PII** — report any fixture files containing real names, email domains, or card numbers that are not Stripe test cards.

## Step 3 — Find orphaned fixtures

Identify fixture files that are no longer imported by any test:

```bash
# For each JSON fixture, check if it's referenced anywhere
grep -r "fixture-name.json" tests/
```

List orphaned fixtures. Do not delete them automatically — list them for human review.

## Step 4 — Find missing cleanup

Tests that seed data without a corresponding cleanup function leave the DB in a dirty state, causing false failures in later tests.

For each seed function found, verify there is an `afterEach` or `afterAll` cleanup call. Flag any that are missing.

## Step 5 — Apply fixes

For each issue found, apply the fix:
1. Replace hardcoded IDs with factory-created or query-based lookups
2. Move hardcoded credentials to environment variables (add to `.env.test.example`)
3. Replace hardcoded base URLs with `process.env.BASE_URL` or `playwright.config.ts` `baseURL`
4. Add missing cleanup functions
5. Extract repeated inline objects into named fixture files

## Step 6 — Recommendations

Summarise findings:
- N hardcoded IDs fixed
- N credential references moved to env vars
- N orphaned fixtures found (list paths for manual review)
- N missing cleanup functions added
- Any PII found (flag as P0 security issue if real PII is present)
