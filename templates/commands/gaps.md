---
command: qakit.gaps
description: Cross-reference feature requirements with the test plan and flag untested scenarios.
---

# /qakit.gaps

Find and list every untested scenario by cross-referencing requirements against the active test plan and test files.

## Context

**Input:** $ARGUMENTS
*(Optional: path to requirements document, Jira epic, or specific feature area. Defaults to `qa-strategy.md` + source files.)*

Before analysing, read:
- `.qakit/memory/qa-strategy.md` — acceptance criteria and user journeys (the "what must work")
- `.qakit/memory/test-plan.md` — planned test coverage
- `.qakit/memory/test-policy.md` — risk thresholds; P0 gaps must be flagged as blockers

Also scan:
- Source files for exported functions, components, or API routes that are not yet covered by tests
- Existing test files for TC-NNN IDs and `describe` / `test` names

## Step 1 — Build requirements list

Extract every testable requirement from `qa-strategy.md`. Assign a short ID if none exists (R-001, R-002, …).

| ID | Requirement / Criterion | Journey | Risk |
|---|---|---|---|

## Step 2 — Build test inventory

List every test that exists, grouped by journey or feature area.

| TC ID / Test name | File | Requirement(s) covered |
|---|---|---|

## Step 3 — Gap matrix

For every requirement in Step 1, mark its coverage:

| Req ID | Description | Status | Missing scenarios |
|---|---|---|---|
| R-001 | … | ✅ / ⚠️ / ❌ | |

Status key:
- ✅ Covered — all scenarios tested
- ⚠️ Partial — happy path only or edge cases absent
- ❌ Missing — zero test coverage

## Step 4 — Untested scenario report

For each ❌ or ⚠️ requirement, write out the specific missing scenarios:

```
Gap #1 [P0 BLOCKER]
Requirement: R-003 — User cannot checkout with expired card
Journey: Checkout flow
Missing: negative path test — card declined response handling
Suggested test: tests/e2e/checkout/payment-errors.spec.ts
```

## Step 5 — Source code scan for untested exports

Scan `src/` (or the project source root) for:
- Functions / methods with no corresponding unit test
- API routes with no integration or contract test
- React/Vue/Angular components with no component test

List the top 5 highest-risk untested items.

## Step 6 — Prioritised action list

Order all gaps by risk (P0 > P1 > P2 > P3) and return a numbered list of tests to write next, each with a target file path.
