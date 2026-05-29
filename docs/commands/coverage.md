# /qakit.coverage

Analyse existing test files and report coverage gaps against requirements.

## Description

Scans the test suite, cross-references every test case against the requirements and acceptance criteria in `.qakit/memory/test-plan.md`, and writes a coverage report to `.qakit/memory/coverage-report.md`. Flags requirements with no linked TC-NNN test, reports the actual pyramid ratio, and identifies over- or under-tested areas.

## Usage

```
/qakit.coverage [<scope>]
```

## Arguments

Optional `<scope>`:
- A file glob (e.g. `tests/e2e/checkout/**`) — limit analysis to a directory
- A journey name (e.g. `"checkout flow"`) — analyse one journey only
- *(empty)* — analyse the full test suite

## Reads from memory

- `.qakit/memory/test-plan.md` — requirement list, TC-NNN assignments, target pyramid ratio
- `.qakit/memory/test-policy.md` — coverage thresholds used to classify gaps as blocking or advisory

## Produces

`.qakit/memory/coverage-report.md` — requirement → TC mapping table, gap list with priority, pyramid ratio vs. target.

## Example

```
/qakit.coverage
```

Output format:
```
TC-001 ✅  Login happy path — tests/e2e/login.spec.ts
TC-002 ✅  Password reset — tests/e2e/password-reset.spec.ts
TC-018 ❌  Rate limiting — no test found  [P1 GAP]

Pyramid: Unit 55% / Integration 20% / E2E 25%  (target: 60/25/15)
```

## Related commands

- `/qakit.gaps` — deeper cross-reference of features vs. test plan
- `/qakit.testplan` — update the plan if the scope has changed
