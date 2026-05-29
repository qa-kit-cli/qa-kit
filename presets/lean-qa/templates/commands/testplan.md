---
command: qakit.testplan
description: Generate a concise test plan (lean-qa preset — minimal ceremony).
---

# /qakit.testplan

Generate a concise test plan and save it to `.qakit/memory/test-plan.md`.

## Context

**Input:** $ARGUMENTS
*(Optional scope or deadline.)*

Read `.qakit/memory/qa-strategy.md` before writing. If it doesn't exist, run `/qakit.strategy` first.

## What to produce

One page. Skip any section that doesn't apply to this project right now.

---

## Scope

Which journeys from `qa-strategy.md` are in scope for this cycle? List them.

## Framework

What are we using? (e.g., Playwright + Jest, Cypress + Vitest, pytest)  
Version: …  
Install check: `npx playwright --version` or equivalent.

## Test count targets

| Layer | Count | Files |
|---|---|---|
| Unit | | |
| Integration | | |
| E2E | | |

Total: N tests. Estimated CI runtime: X minutes.

## File layout

```
tests/
  unit/
  e2e/
    <journey>.spec.ts
```

## Data

What test data is needed? Where does it live? How is state reset between runs?

## CI trigger

| Test type | Trigger | Gate |
|---|---|---|
| Unit + integration | Every PR | Block merge |
| E2E | Push to main | Block deploy |

---

**Save to `.qakit/memory/test-plan.md`.**
