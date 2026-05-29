---
command: qakit.policy
description: Create or update test-policy.md — the project QA governance document.
---

# /qakit.policy

Create or update `.qakit/memory/test-policy.md` — the project's QA constitution.

## Context

**Input:** $ARGUMENTS
*(Optional: specific sections to update, e.g. "update coverage thresholds to 80% unit, add cypress to approved frameworks". Defaults to creating a full policy from scratch.)*

Before writing, read:
- `.qakit/memory/qa-strategy.md` — to infer the risk profile and framework choices already made
- `.qakit/memory/test-plan.md` — to extract the environment matrix and framework versions
- `.qakit/memory/test-policy.md` — if it exists, update only the sections specified in `$ARGUMENTS`; preserve the rest

If generating from scratch, inspect the project's `package.json` / `pyproject.toml` / `pom.xml` for installed testing frameworks, and the CI config files for existing gates.

## What to produce

A `test-policy.md` that every team member and AI agent can use as a single source of truth.

---

## Coverage Thresholds

Specify minimum passing thresholds. If none exist in the project today, recommend sensible defaults based on the risk profile:

| Metric | Threshold | Tool |
|---|---|---|
| Unit line coverage | ≥ X% | jest --coverage / pytest-cov |
| Unit branch coverage | ≥ X% | |
| Integration coverage | ≥ X% | |
| Critical E2E paths | 100% | Playwright / Cypress |

List the named "critical E2E paths" by journey name from `qa-strategy.md`.

## Approved Frameworks

List exactly which frameworks are approved for each test type. Unapproved frameworks require a policy amendment via this command.

| Test type | Approved framework(s) | Version |
|---|---|---|
| E2E | | |
| Component | | |
| Unit | | |
| API / Contract | | |
| Visual regression | | |
| Accessibility | | |
| Load / Performance | | |

## Environment Matrix

| Browser | Version | OS | Priority |
|---|---|---|---|
| | | | P0 / P1 / P2 |

Note: P0 environments must pass in CI before merge. P1/P2 may run nightly.

## Test Organisation

- **File naming:** `<feature>.spec.ts` / `<module>_test.py`
- **Directory layout:** `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **POM requirement:** Page Object Models required for all E2E flows touching ≥ 3 pages
- **TC-NNN IDs:** required in test titles for all E2E and integration tests (`TC-001`, `TC-002`, …)
- **Import style:** use `@playwright/test` named imports; no global `page` in Playwright

## Flakiness Policy

- **Maximum flakiness rate:** X% over a rolling 7-day window (recommend ≤ 2%)
- **Retry strategy:** N retries in CI (recommend 2); zero retries locally
- **Quarantine threshold:** tests failing in > Y% of runs are quarantined pending fix within Z days
- **Root cause required:** all flaky tests must have a root-cause comment before re-enabling

## Defect Severity Taxonomy

| Severity | Definition | SLA |
|---|---|---|
| P0 — Critical | Data loss, auth bypass, payments broken, app unlaunchable | Fix before next deploy |
| P1 — High | Primary user journey broken, major data corruption | Fix within 24 h |
| P2 — Medium | Secondary journey degraded, workaround exists | Fix within sprint |
| P3 — Low | Cosmetic, minor UX, no functional impact | Backlog |

## CI/CD Gates

| Gate | Condition | Action on failure |
|---|---|---|
| PR gate | Unit + integration must pass | Block merge |
| PR gate | Coverage must not drop below threshold | Block merge |
| Main gate | Full E2E suite on P0 browsers | Block deploy |
| Release gate | Full matrix + visual + a11y | Block release |

---

**Save to `.qakit/memory/test-policy.md`.**
After saving, print a one-line summary of what changed.
