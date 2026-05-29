---
command: qakit.regression
description: Build or update the regression suite with P0/P1/P2 tiers and quarantine tracking.
---

# /qakit.regression

Build or update the regression suite.

Read `.qakit/memory/test-plan.md`, `.qakit/memory/traceability-matrix.md` (if present), and existing test files, then generate or update the regression suite definition.

## Output format

Save to `.qakit/memory/regression-suite.md`:

```markdown
# Regression Suite

## P0 — Smoke (run on every commit, < 5 min)
| TC ID | Test Name | File | Framework | Tags |
|-------|-----------|------|-----------|------|
| TC-001 | Home page loads | tests/e2e/home.spec.ts | Playwright | smoke, p0 |

## P1 — Critical Path (run on PR merge, < 15 min)
| TC ID | Test Name | File | Framework | Tags |
|-------|-----------|------|-----------|------|
| TC-010 | Full checkout flow | tests/e2e/checkout.spec.ts | Playwright | critical, p1 |

## P2 — Full Regression (run nightly, < 60 min)
| TC ID | Test Name | File | Framework | Tags |
|-------|-----------|------|-----------|------|
| TC-020 | Admin dashboard | tests/e2e/admin.spec.ts | Playwright | regression, p2 |

## Quarantined (flaky — excluded from blocking gates)
| TC ID | Test Name | File | Reason | Owner | Deadline |
|-------|-----------|------|--------|-------|----------|
| TC-099 | Notification timing | tests/e2e/notif.spec.ts | Race condition | @dev | 2025-07-01 |

## Deprecated (remove after [date])
| TC ID | Test Name | Reason |
|-------|-----------|--------|
| TC-050 | Legacy login | Replaced by TC-001 |
```

## Rules

- Assign tests to tiers based on risk, speed, and business criticality.
- P0 must run in < 5 minutes total.
- Quarantined tests must have an owner and a resolution deadline.
- Flag deprecated tests for removal.
- Identify gaps where high-risk areas lack regression coverage.

$ARGUMENTS
