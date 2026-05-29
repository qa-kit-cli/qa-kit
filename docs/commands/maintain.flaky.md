# /qakit.maintain.flaky

Diagnose a flaky test: identify root cause, suggest a retry strategy or deterministic fix.

## Description

Analyses a failing or intermittently-failing test, classifies the flakiness pattern (timing, state leakage, environment sensitivity, network dependency, selector instability, data dependency, concurrency), applies a deterministic fix where possible, and documents the root cause. Falls back to quarantine with a linked issue if the fix requires a larger refactor.

## Usage

```
/qakit.maintain.flaky <test identifier>
```

## Arguments

- Test file path, test name, TC-NNN ID, or pasted failure log
- Examples: `tests/e2e/checkout/payment.spec.ts`, `TC-042`, `"login.spec.ts fails intermittently on Firefox"`

## Reads from memory

- `.qakit/memory/test-policy.md` — max retry count, quarantine threshold and process, resolution SLA

## Produces

Inline report:
- Root cause classification and explanation
- The minimal code change (diff) that makes the test deterministic
- Or: quarantine tag + `test.skip` annotation with issue link if not fixable now
- Verification commands to confirm the fix is stable

## Example

```
/qakit.maintain.flaky tests/e2e/auth/mfa.spec.ts
```

Common fixes applied:
- `await page.waitForResponse(…)` replacing `page.waitForTimeout(N)`
- `test.beforeEach` state isolation replacing inter-test dependencies
- `page.getByRole(…)` replacing fragile CSS-class selectors
- `page.route(…)` mock replacing real third-party HTTP calls

## Related commands

- `/qakit.maintain.refactor` — broader refactor of the test file after fixing flakiness
- `/qakit.maintain.data` — fix data-dependency flakiness caused by hardcoded test data
