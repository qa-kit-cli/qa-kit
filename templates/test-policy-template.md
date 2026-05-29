# Test Policy

> This document is the QA governance authority for this project.
> All test plans, CI configurations, and agent-generated tests must align with the rules below.
> Update this file when project standards change; do not deviate silently.

**Version:** 1.0  
**Owner:** <!-- @qa-lead -->  
**Last Updated:** <!-- YYYY-MM-DD -->

---

## Coverage Thresholds

| Suite type | Minimum threshold | Enforcement |
|---|---|---|
| Unit (lines) | 80% | CI gate — PR fails below threshold |
| Unit (branches) | 70% | CI gate |
| Integration | 60% | CI gate |
| E2E critical paths | All P1 journeys covered | Manual audit via `qakit.coverage` |

**Measurement tool:** Jest `--coverage` for unit/integration; Playwright coverage plugin for E2E.

> The `coverage-gate` QA Kit extension enforces these thresholds automatically in CI.

---

## Approved Frameworks

| Test type | Approved framework(s) | Notes |
|---|---|---|
| E2E | Playwright ≥ 1.40 | TypeScript only; `page.getByRole` locators required |
| Unit | Jest ≥ 29 | `ts-jest` transform; no `any` casts in test files |
| Component | Vitest + Testing Library | For Vite-based frontends only |
| API contract | Supertest or Playwright APIRequestContext | No raw `axios` in tests |
| Visual regression | Playwright screenshots | Percy is optional for PR review; not a CI gate |
| Accessibility | axe-core via `@axe-core/playwright` | Run against all P1 pages |

**Unapproved:** Cypress (migrate existing Cypress tests to Playwright by <!-- YYYY-MM-DD -->), Selenium (legacy only — no new Selenium tests).

---

## Environment Matrix

E2E tests must pass on the following matrix before a release is approved:

| Browser | Version | OS | Required for |
|---|---|---|---|
| Chromium | Latest stable | ubuntu-latest | All PRs + release |
| Firefox | Latest stable | ubuntu-latest | Merge to main + release |
| WebKit | Latest stable | ubuntu-latest | Merge to main + release |

**Mobile:** Not in scope for v1.x. Tracked as P3 for v2.0.

---

## Test Organization

**Directory structure:**
```
tests/
├── unit/           # *.test.ts  — pure logic, no I/O
├── integration/    # *.test.ts  — real services via Docker Compose
├── e2e/            # *.spec.ts  — full browser flows
├── fixtures/       # Factory functions; no hardcoded IDs
└── pages/          # Page Object Model classes (one file per page/component)
```

**Naming rules:**
- Test files: `<subject>.<type>.ts` (e.g. `auth.service.test.ts`, `login.spec.ts`)
- POM classes: `<PageName>Page.ts` (e.g. `LoginPage.ts`)
- Fixtures: named exports, no default exports

**Test ID scheme:** Every E2E and integration test case carries a canonical ID: `TC-001`, `TC-002`, …
IDs are assigned in `test-plan.md` and must not be reused after a test is deleted.

---

## Flakiness Policy

- **Retry limit:** Maximum 2 retries in CI (`retries: 2` in Playwright config). Unit tests: 0 retries.
- **Quarantine threshold:** A test that fails intermittently in ≥ 3 of the last 10 CI runs is declared flaky and must be quarantined (tagged `@flaky`) within 1 business day.
- **Quarantine process:** Tag with `@flaky`, open a bug (P2 minimum), link TC-ID. Quarantined tests do not block the PR gate but are reported in the CI summary.
- **Resolution SLA:** P1 flaky tests resolved within 5 business days; P2 within 2 sprints.
- **Root cause tool:** Use `qakit.maintain.flaky` for systematic diagnosis.

---

## Defect Severity Taxonomy

| Severity | Definition | Examples | SLA |
|---|---|---|---|
| **P0 — Critical** | Production is broken; data loss or security breach possible | Auth bypass, data corruption, service down | Fix same day; hotfix release |
| **P1 — High** | Core user journey is broken with no workaround | Login fails for all users, checkout disabled | Fix within 1 sprint |
| **P2 — Medium** | Feature degraded; workaround exists | Error message misleading, pagination off by 1 | Fix within 2 sprints |
| **P3 — Low** | Cosmetic or minor inconvenience | Tooltip typo, minor layout shift | Fix when capacity allows |

**Defect tracking:** All P0/P1 defects require a linked bug report (`qakit.review.bugreport` format) and a linked failing test case before they are closed.

---

## CI/CD Gates

| Gate | Trigger | Tests run | Blocks |
|---|---|---|---|
| **PR gate** | Push to any PR branch | Unit + Integration + E2E (Chromium) | Merge |
| **Main gate** | Merge to `main` | Full browser matrix | Deploy to staging |
| **Release gate** | Tag `v*.*.*` | Full matrix + staging smoke tests | Publish to PyPI / deploy to production |

**Coverage enforcement:** PR gate fails if unit coverage drops below the threshold defined above.

**Artefact retention:**
- JUnit XML: 30 days
- HTML report: 30 days
- Playwright traces (failure only): 7 days
