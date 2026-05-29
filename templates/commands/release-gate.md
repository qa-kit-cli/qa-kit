---
command: qakit.release-gate
description: Decide ship/no-ship based on coverage, test results, defects, and risk.
---

# /qakit.release-gate

Make a release gate decision.

Read `.qakit/memory/test-plan.md`, `.qakit/memory/traceability-matrix.md`, `.qakit/memory/defect-summary.md`, `.qakit/memory/regression-suite.md`, and CI status, then produce a release gate decision.

## Output format

Save to `.qakit/memory/release-gate.md`:

```markdown
# Release Gate Report

## Release: [version / feature name]
## Date: [YYYY-MM-DD]
## Decision: 🟢 SHIP / 🔴 NO-SHIP / 🟡 CONDITIONAL SHIP

---

## Decision Summary
[One paragraph: what the data shows and why the decision was reached]

## Conditions (if CONDITIONAL SHIP)
- [ ] Condition 1
- [ ] Condition 2

---

## Gate Inputs

### Coverage
| Metric | Actual | Threshold | Status |
|--------|--------|-----------|--------|
| Unit test coverage | 0% | 80% | ❌ |
| E2E critical path coverage | 0% | 100% | ❌ |

### Test Results
| Suite | Passed | Failed | Skipped | Flaky |
|-------|--------|--------|---------|-------|
| P0 Smoke | 0 | 0 | 0 | 0 |
| P1 Critical | 0 | 0 | 0 | 0 |

### Defects
| Severity | Open | Accepted Risk | Blocking |
|----------|------|---------------|----------|
| P0 Critical | 0 | 0 | Yes |
| P1 High | 0 | 0 | If > 3 |

### Traceability
- Requirements covered: 0/0 (0%)
- High-risk requirements with full coverage: 0/0

### Risk Assessment
| Area | Risk Level | Coverage | Recommendation |
|------|------------|----------|----------------|
```

## Scoring rules

- **SHIP**: All P0 tests pass, coverage ≥ thresholds, no blocking P0 defects, all high-risk requirements covered.
- **NO-SHIP**: Any P0 test failing, any blocking defect, critical coverage gap.
- **CONDITIONAL SHIP**: Minor gaps with accepted risk, stakeholder sign-off required.

Be explicit and honest. Err on the side of caution for P0 risk areas.

$ARGUMENTS
