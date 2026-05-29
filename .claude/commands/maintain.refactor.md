---
command: qakit.maintain.refactor
description: Refactor an existing test file to follow current framework conventions and reduce duplication.
---

# /qakit.maintain.refactor

Refactor the specified test file to follow current conventions without changing what is being tested.

## Context

**Input:** $ARGUMENTS
*(Provide the test file path or directory to refactor. Example: "tests/e2e/checkout.spec.ts" or "tests/unit/".)*

Before refactoring, read:
- `.qakit/memory/test-policy.md` — approved conventions: locators, file naming, TC-NNN IDs, POM requirement
- The source file(s) at `$ARGUMENTS`

**Golden rule:** the refactor must not change which scenarios are tested or what the assertions verify. Run the tests before and after and confirm the same tests pass.

## Step 1 — Audit the current file

Identify all convention violations and code quality issues:

**Locator issues**
- `page.$('.submit-btn')` → `page.getByRole('button', { name: 'Submit' })`
- `cy.get('.user-email')` → `cy.findByLabelText('Email address')`
- Position-based: `page.locator('div:nth-child(3)')` → use a role or test ID

**Timing issues**
- `page.waitForTimeout(2000)` → replace with `waitForResponse` or `expect(locator).toBeVisible()`
- `cy.wait(3000)` → `cy.intercept(…).as('request'); cy.wait('@request')`

**Duplication**
- Repeated setup code not in `beforeEach` or a shared fixture
- Same page interaction sequence repeated across 3+ tests → extract to a helper or POM method

**Missing TC-NNN IDs**
- Tests without TC-NNN IDs in their title → assign the next available IDs from `test-plan.md`

**Assertions**
- `expect(await locator.isVisible()).toBe(true)` → `await expect(locator).toBeVisible()`
- Multiple property assertions that could use `toMatchObject`

**Missing test.step() wrapping (Playwright)**
- Long tests with no structural steps → wrap into Arrange / Act / Assert `test.step()` blocks

## Step 2 — Apply refactors

For each issue found, apply the fix. Show a before/after diff for each change.

**Extract POM** (if required by policy for this page):
```typescript
// Before: inline locators scattered through every test
const email = page.locator('#email');
await email.fill('user@example.com');

// After: POM method
const loginPage = new LoginPage(page);
await loginPage.fillEmail('user@example.com');
```

**Replace fragile locators:**
```typescript
// Before
await page.click('.checkout-btn');

// After
await page.getByRole('button', { name: 'Proceed to checkout' }).click();
```

**Consolidate setup:**
```typescript
// Before: same 3 lines duplicated in every test
await page.goto('/checkout');
await page.fill('#email', 'test@example.com');
await page.click('.login-btn');

// After: extracted to beforeEach or a shared fixture
test.beforeEach(async ({ page }) => {
  await loginPage.loginAs({ email: 'test@example.com', password: 'Password1!' });
  await page.goto('/checkout');
});
```

**Add TC-NNN IDs:**
```typescript
// Before
test('adds item to cart', …)

// After
test('TC-017 adds item to cart from product page', …)
```

## Step 3 — Verify no behaviour change

Run the test file before and after:
```bash
npx playwright test tests/e2e/checkout.spec.ts --reporter=list
```
Confirm: same number of tests, same pass/fail results.

## Step 4 — Summary

Print:
- N locators updated
- N timing issues removed
- N TC-NNN IDs assigned
- N duplications extracted
- Whether a POM class was created or updated
