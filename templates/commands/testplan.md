---
command: qakit.testplan
description: Produce a structured test plan from the active QA strategy.
---

# /qakit.testplan

Generate a structured test plan and save it to `.qakit/memory/test-plan.md`.

## Context

**Input:** $ARGUMENTS
*(Optional: scope override, sprint deadline, or specific user journeys to include/exclude.)*

Before writing, read:
- `.qakit/memory/qa-strategy.md` — the source of truth for journeys, risk levels, and acceptance criteria
- `.qakit/memory/test-policy.md` — coverage thresholds, approved frameworks, CI/CD gates, and flakiness policy

If `qa-strategy.md` does not exist, run `/qakit.strategy` first.

## What to produce

A concrete, actionable test plan. Every section must be specific to this project — no generic filler.

---

## Summary

- **Scope:** which user journeys are in scope (by journey name from `qa-strategy.md`)
- **Objectives:** what "done" looks like (coverage %, passing gates, specific scenarios covered)
- **Success metrics:** numeric targets (e.g., unit coverage ≥ threshold from policy, zero P0 flaky tests)

## Technical Context

- Framework versions in use (Playwright vX.Y, Jest vX.Y, etc.)
- Node / Python version
- CI environment (GitHub Actions / Jenkins / local)
- Any relevant constraints (monorepo, Docker required, secrets needed)

## Policy Check

Confirm alignment with `test-policy.md` before proceeding. Call out any deviations:
- [ ] Coverage thresholds met by this plan
- [ ] Approved frameworks only
- [ ] Environment matrix satisfied
- [ ] CI/CD gates respected

## Test Architecture

State the planned pyramid ratio and justify it against the risk profile:

| Layer | Target % | Count (est.) | Justification |
|---|---|---|---|
| Unit | | | |
| Integration | | | |
| E2E | | | |
| Visual | | | |
| A11y | | | |

## Test Suite Layout

Describe the directory structure for test files:
```
tests/
  unit/
  integration/
  e2e/
    pages/          # Page Object Models
    fixtures/
    specs/
```
State file naming convention (e.g., `*.spec.ts`, `*_test.py`).

## Environment Matrix

| Browser/Platform | Version | Priority |
|---|---|---|
| | | |

Mirror the matrix from `test-policy.md`. Flag any deviations.

## Data Model

- Fixture files and their locations
- Factory functions needed
- Seed script strategy
- How to reset state between tests

## CI/CD Integration

For each test layer, state which CI stage runs it and when:

| Test type | CI stage | Trigger | Failure action |
|---|---|---|---|
| Unit | | | |
| Integration | | | |
| E2E | | | |

---

**Save the completed document to `.qakit/memory/test-plan.md`.**
If `.qakit/memory/test-plan.md` already exists, update it in place.
