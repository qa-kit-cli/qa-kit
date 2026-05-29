# /qakit.maintain.data

Audit and clean up test data: orphaned fixtures, hardcoded values, and environment coupling.

## Description

Scans the test suite for data quality issues: hardcoded IDs or emails, fixture files not referenced by any test, test data that leaks between tests (missing cleanup), and environment-specific values baked into test code. Produces a remediation plan and applies safe fixes.

## Usage

```
/qakit.maintain.data [<scope>]
```

## Arguments

Optional `<scope>`:
- Directory or file glob to limit the audit
- *(empty)* — scans the entire `tests/` directory

## Reads from memory

- `.qakit/memory/test-policy.md` — PII rules, fixture strategy, environment isolation requirements
- `.qakit/memory/test-plan.md` — Data Model section: approved fixture names and factory patterns

## Produces

Inline audit report:

```
Hardcoded values found:
  tests/e2e/login.spec.ts:12  "user-123@real-domain.com"  → replace with createUser()
  tests/integration/order.test.ts:34  orderId: "abc-456"  → replace with factory

Orphaned fixtures (no test imports them):
  tests/fixtures/legacy-cart.json  → safe to delete

State leak risk:
  tests/e2e/profile.spec.ts  — creates a user in beforeAll but has no afterAll cleanup
```

Applies safe fixes (factory replacements, `afterEach` cleanup) and reports what still needs manual attention.

## Example

```
/qakit.maintain.data
```

## Related commands

- `/qakit.write.fixtures` — generate clean factory functions to replace hardcoded values
- `/qakit.maintain.refactor` — broader refactoring after cleaning up data issues
