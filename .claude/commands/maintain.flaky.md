---
command: qakit.maintain.flaky
description: Diagnose a flaky test and produce a deterministic fix or retry strategy.
---

# /qakit.maintain.flaky

Diagnose the root cause of a flaky test and fix it or quarantine it with a documented plan.

## Context

**Input:** $ARGUMENTS
*(Provide the test file path, test name, or TC-NNN ID. Example: "tests/e2e/checkout/payment.spec.ts TC-042" or paste the failure log.)*

Before analysing, read:
- `.qakit/memory/test-policy.md` — flakiness policy: max flakiness rate, retry limit, quarantine threshold, root-cause requirement
- The test file at `$ARGUMENTS`
- Any CI failure logs or screenshots/traces provided

## Step 1 — Classify the flakiness pattern

Determine which category the failure falls into by reading the test code and failure evidence:

| Category | Symptoms | Common causes |
|---|---|---|
| **Timing / race condition** | Passes locally, fails in CI; failures are non-deterministic | Missing `await`, polling without timeout, relying on implicit ordering |
| **State leakage** | Passes in isolation, fails in suite | Shared mutable state, DB not reset, cookies/localStorage not cleared |
| **Environment sensitivity** | Passes in one browser/OS, fails in another | CSS layout differences, font rendering, locale-specific date formats |
| **Network dependency** | Fails on slow connections or under load | No mock for external API, real HTTP calls with no retry, timeout too short |
| **Selector instability** | Fails after UI changes that weren't test-breaking | Fragile CSS class selector, position-based XPath, text that changes per locale |
| **Data dependency** | Fails when database state differs | Test relies on existing data without seeding, hardcoded IDs |
| **Concurrency** | Fails under parallel execution | Test writes to a shared fixture file, shared DB row, port conflict |

## Step 2 — Reproduce and confirm

Provide a command to reproduce the failure reliably:

```bash
# Run the test 10 times to confirm intermittent failure rate
npx playwright test "TC-042" --repeat-each=10 --reporter=list

# Or with Jest
jest --testPathPattern="payment.test.ts" --runInBand --count=10
```

State the observed failure rate: fails X out of Y runs.

## Step 3 — Root cause analysis

Read the test code carefully. For each suspicious line, explain:
- What assumption it makes
- Why that assumption can fail intermittently

**Timing example:**
```typescript
// Flaky: implicit timing assumption
await page.click('#submit');
const text = await page.textContent('.confirmation'); // may run before DOM updates

// Fixed: wait for the expected state
await page.click('#submit');
await expect(page.locator('.confirmation')).toBeVisible();
const text = await page.textContent('.confirmation');
```

**State leakage example:**
```typescript
// Flaky: relies on previous test's data
test('TC-042 shows order history', async ({ page }) => {
  await page.goto('/orders'); // assumes orders exist from a previous test
});

// Fixed: seed the state explicitly
test.beforeEach(async ({ page, request }) => {
  await request.post('/api/test/seed', { data: { scenario: 'order-history' } });
});
```

## Step 4 — Apply the fix

Make the minimal change to make the test deterministic. Options in order of preference:

1. **Remove the race condition** — add proper `await`, use `waitForResponse`, replace `waitForTimeout`
2. **Isolate state** — add `beforeEach`/`afterEach` to reset shared state
3. **Replace fragile locator** — use `getByRole`, `getByLabel`, or `getByTestId`
4. **Mock the external dependency** — replace real HTTP call with `page.route()` or Jest mock
5. **Add retry with root cause comment** — only if the race is in external infrastructure outside the test's control:

```typescript
test.describe.configure({ retries: 2 }); // maximum from test-policy.md
// FLAKY-ROOT-CAUSE: third-party payment sandbox occasionally returns 503 under load;
// retrying is acceptable here because the test cannot control the external service.
```

## Step 5 — Quarantine (if not fixable now)

If a fix requires a larger refactor that cannot be done in this session:

1. Add the quarantine marker to the test:
```typescript
test.skip(process.env.CI === 'true', 'QUARANTINED: flaky due to state leakage — tracked in #issue-number');
```
2. Add a comment with: root cause, issue link, estimated fix effort, and quarantine date
3. Update `.qakit/memory/test-policy.md` quarantine list

## Output

After making the fix (or applying quarantine), print:
- Root cause classification
- Change made (diff summary)
- Commands to verify the fix is stable
