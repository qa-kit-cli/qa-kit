---
command: qakit.coverage
description: Analyse existing tests and report coverage gaps against the active test plan.
---

# /qakit.coverage

Analyse the current test suite and produce a coverage gap report.

## Context

**Input:** $ARGUMENTS
*(Optional: path to scan, e.g. `tests/e2e/checkout` or a specific requirement ID. Defaults to full test suite.)*

Before analysing, read:
- `.qakit/memory/test-plan.md` — acceptance criteria and user journeys that must be covered
- `.qakit/memory/test-policy.md` — coverage thresholds (unit %, integration %, critical E2E paths)
- `.qakit/memory/qa-strategy.md` — risk levels per journey (P0–P3 gaps are most urgent)

## Step 1 — Inventory existing tests

Walk all test directories. For each test file, extract:
- File path
- Test IDs present (TC-NNN pattern if assigned)
- Test names / describe blocks
- Which user journey or requirement they appear to cover (infer from naming and content)

Produce a table:

| Test file | TC IDs | Journey covered | Type (unit/int/e2e/a11y/visual/api) |
|---|---|---|---|

## Step 2 — Map against test plan requirements

For each user journey and acceptance criterion in `test-plan.md`:
- ✅ **Covered** — at least one test verifies this criterion
- ⚠️ **Partially covered** — happy path only, edge cases missing
- ❌ **Not covered** — no test exists

| Journey / Criterion | Coverage | Test(s) | Gap description |
|---|---|---|---|

## Step 3 — Calculate pyramid ratio

| Layer | Target % | Actual count | Actual % | Delta |
|---|---|---|---|---|
| Unit | | | | |
| Integration | | | | |
| E2E | | | | |
| Visual | | | | |
| A11y | | | | |

## Step 4 — Prioritised gap list

List all gaps ordered by risk (P0 first):

1. `[P0]` Journey: … — Missing: …
2. `[P1]` Journey: … — Missing: …

## Step 5 — Threshold check

Compare actual numbers to thresholds from `test-policy.md`:
- Unit coverage: X% (threshold: Y%) → PASS / FAIL
- Critical E2E paths: N/M covered → PASS / FAIL

## Step 6 — Next action

Recommend the single highest-priority test to write next, with the target file path and a one-sentence description of what it should assert.
