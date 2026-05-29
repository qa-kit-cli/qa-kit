---
command: qakit.strategy
description: Generate a concise QA strategy (lean-qa preset — minimal ceremony).
---

# /qakit.strategy

Generate a concise QA strategy and save it to `.qakit/memory/qa-strategy.md`.

## Context

**Input:** $ARGUMENTS
*(Feature description, PRD link, or Jira ticket.)*

Read `.qakit/memory/test-policy.md` if it exists — honour any defined frameworks or thresholds.

## What to produce

A short, scannable strategy. Skip sections that don't apply. No filler.

---

## What we're testing

One paragraph: what the feature does and who uses it.

**Risk level:** P0 / P1 / P2 / P3 — and why.

## User journeys (P0/P1 only)

List the journeys worth testing, highest risk first:

1. `[P0]` **Journey name** — start state → end state
2. `[P1]` **Journey name** — start state → end state

Skip P2/P3 journeys unless time allows.

## Test types needed

Check what applies:
- [ ] Unit — logic worth isolating
- [ ] Integration — service boundaries to verify
- [ ] E2E — user journeys above that need a browser
- [ ] API — contracts to verify
- [ ] A11y — if user-facing UI is involved

## Acceptance criteria (must-pass)

One line per criterion. If it can't be verified automatically, it's out of scope:
- Given … when … then …

## Out of scope

What we're explicitly not testing this cycle.

---

**Save to `.qakit/memory/qa-strategy.md`.**
