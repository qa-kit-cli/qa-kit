---
command: qakit.review.pr
description: Review a pull request from a QA perspective — coverage delta, missing edge cases, risk areas.
---

# /qakit.review.pr

Review the provided pull request from a QA perspective.

## Context

**Input:** $ARGUMENTS
*(Provide the PR number, diff, or branch name. Example: "#142" or "feature/checkout-refactor".)*

Before reviewing, read:
- `.qakit/memory/test-policy.md` — coverage thresholds and CI/CD gates
- `.qakit/memory/qa-strategy.md` — risk levels for the affected feature areas
- `.qakit/memory/test-plan.md` — which TC-NNN tests should cover these changes

Read the PR diff. Focus on:
- All changed source files (`src/`, `app/`, `lib/`)
- All changed or added test files
- CI config changes

## Review dimensions

### 1. Risk assessment

Classify the change's risk level:

| Changed area | Risk | Reason |
|---|---|---|
| Auth / session logic | P0 | … |
| Payment / billing | P0 | … |
| Core data mutations | P1 | … |
| UI-only changes | P3 | … |

State the overall PR risk level and its implication for the required review depth.

### 2. Test coverage delta

For every source file changed, check whether a corresponding test change exists:

| Source file changed | Lines changed | Has test change? | Assessment |
|---|---|---|---|
| `src/checkout/PaymentForm.tsx` | 45 | Yes — `payment.spec.ts` | ✅ |
| `src/utils/priceCalc.ts` | 12 | No | ❌ Missing |

For uncovered changes, state what scenarios should be tested.

### 3. Missing test scenarios

Read the changed code and enumerate scenarios not covered by the PR's tests:

- **Happy path covered?** ✅/❌
- **Error paths covered?** List uncovered error states (e.g., network timeout, 4xx responses)
- **Edge cases covered?** Boundary values, null inputs, empty collections
- **Concurrent/race conditions?** If the change involves async operations, are race conditions tested?

### 4. Test quality review

For each test file added or modified in the PR, check:

- [ ] Uses `getByRole`/`getByLabel` locators (not CSS classes or XPath)
- [ ] No `waitForTimeout` or `cy.wait(N)` calls
- [ ] All network interactions are mocked or use `waitForResponse`
- [ ] `beforeEach`/`afterEach` properly isolates state
- [ ] TC-NNN IDs present in E2E and integration test titles
- [ ] Assertions are specific (not just `toBeVisible()` — also check content, state, or network payload)

### 5. Coverage gate prediction

Will this PR pass the coverage gate? Estimate:
- Lines added to source: N
- Lines covered by new tests: M
- Predicted coverage delta: ±X%
- Gate status: PASS / FAIL / AT RISK

### 6. Regression risk

Does this change affect code paths tested by existing tests outside this PR? List any:
- Tests that exercise the changed code paths
- Whether those tests need updating

## Verdict

**Approve / Request changes / Comment**

State your QA verdict with specific action items. Format required changes as a checklist:

- [ ] Add test for `null` productId case in `CartService.addItem()`
- [ ] TC-042 is missing an assertion on the response body — it only checks status code
- [ ] Replace `cy.wait(2000)` in `checkout.cy.ts:88` with `cy.wait('@placeOrder')`
