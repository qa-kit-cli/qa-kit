# /qakit.pyramid

Analyse the project's test pyramid ratio and recommend adjustments.

## Description

Counts unit, integration, and E2E tests in the project, compares the ratio against the target pyramid in `.qakit/memory/test-plan.md` and the thresholds in `.qakit/memory/test-policy.md`, and recommends concrete changes — tests to add, tests to demote (E2E → integration), or duplicates to remove.

## Usage

```
/qakit.pyramid [<scope>]
```

## Arguments

Optional `<scope>`:
- A directory glob (e.g. `tests/`) to limit the analysis
- *(empty)* — scans the entire project

## Reads from memory

- `.qakit/memory/test-plan.md` — target pyramid ratio (unit/integration/E2E percentages)
- `.qakit/memory/test-policy.md` — minimum coverage thresholds per layer

## Produces

A pyramid analysis report printed inline:

```
Current pyramid:
  Unit        48%  (38 tests)   target: 60%  ⚠ below target
  Integration 17%  (13 tests)   target: 25%  ⚠ below target
  E2E         35%  (28 tests)   target: 15%  ❌ over-indexed

Recommendations:
  1. Convert 8 E2E tests that cover pure business logic → Jest unit tests
  2. Add 6 integration tests for the DB session store (currently untested at integration layer)
  3. Net change: +14 unit, +6 integration, -8 E2E → target ratio achieved
```

## Example

```
/qakit.pyramid
```

## Related commands

- `/qakit.coverage` — detailed requirement → test mapping
- `/qakit.testplan` — update the target pyramid if the project's needs have changed
