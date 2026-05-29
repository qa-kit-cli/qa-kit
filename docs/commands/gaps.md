# /qakit.gaps

Cross-reference feature requirements with the test plan and flag untested scenarios.

## Description

Reads the feature specification (or the current codebase) alongside `.qakit/memory/test-plan.md` and identifies scenarios that are described in the requirements but have no corresponding test case. Produces an actionable gap list ordered by business risk.

Complements `/qakit.coverage` (which scans existing test files) by working from the requirements side — it catches scenarios that were never planned, not just tests that were planned but not written.

## Usage

```
/qakit.gaps [<input>]
```

## Arguments

Optional `<input>`:
- Feature spec, PRD text, or Jira ticket to cross-reference
- *(empty)* — uses `.qakit/memory/qa-strategy.md` as the requirements source

## Reads from memory

- `.qakit/memory/qa-strategy.md` — source of requirements and acceptance criteria
- `.qakit/memory/test-plan.md` — existing TC-NNN assignments

## Produces

A gap analysis table printed inline. Each gap includes:
- The untested scenario
- Its risk priority (P0–P3)
- A suggested TC-NNN ID for the missing test
- The recommended command to write it (e.g. `/qakit.write.playwright`)

## Example

```
/qakit.gaps
```

## Related commands

- `/qakit.coverage` — scans actual test files for missing coverage
- `/qakit.strategy` — update the strategy if new requirements surface
