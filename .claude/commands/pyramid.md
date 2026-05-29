---
command: qakit.pyramid
description: Analyse the project's test pyramid ratio and recommend adjustments.
---

# /qakit.pyramid

Analyse the current test pyramid (unit / integration / e2e ratio) and recommend adjustments.

## Context

**Input:** $ARGUMENTS
*(Optional: target ratio override, e.g. "70/20/10" for unit/integration/e2e, or a specific area to analyse.)*

Before analysing, read:
- `.qakit/memory/test-policy.md` — target ratios and coverage thresholds if set
- `.qakit/memory/test-plan.md` — planned pyramid from the test plan

## Step 1 — Count existing tests

Scan all test files and categorise each test by type:

| Category | How to identify |
|---|---|
| **Unit** | Pure function tests, no network/FS/DB, typically `*.test.ts`, `*_test.py` in `unit/` or co-located |
| **Integration** | Tests that cross module boundaries, use a real DB or real HTTP client |
| **E2E** | Browser-based tests (`*.spec.ts` with Playwright/Cypress), full user flow |
| **Visual** | Screenshot comparison tests |
| **A11y** | `axe` / `checkA11y` assertions |
| **API/Contract** | Supertest, Playwright APIRequestContext, Pact |
| **Performance** | k6, Lighthouse, WebPageTest |

Produce a count table:

| Layer | File count | Test count | % of total |
|---|---|---|---|
| Unit | | | |
| Integration | | | |
| E2E | | | |
| Visual | | | |
| A11y | | | |
| API | | | |

## Step 2 — Compare to targets

Compare actual ratio to:
1. Targets in `test-policy.md` (if defined)
2. The recommended ratio for this project's risk profile (infer from `qa-strategy.md`)
3. The classic ideal: ~70% unit / ~20% integration / ~10% E2E

| Layer | Actual % | Target % | Status |
|---|---|---|---|
| | | | Over / Under / OK |

## Step 3 — Diagnose imbalances

For each layer that is significantly over or under target, explain the likely cause and risk:

**Too many E2E, too few unit tests:**
- Slow CI, brittle suite, high maintenance cost
- Recommendation: identify which E2E tests cover logic that could be unit-tested

**Too many unit tests, no E2E:**
- Integration confidence gap; works in isolation, breaks in production
- Recommendation: add smoke E2E tests for top 3 P0 user journeys

**Missing integration layer:**
- Mocked unit tests may hide contract mismatches
- Recommendation: add integration tests for DB layer and external API calls

## Step 4 — Concrete recommendations

List 3–5 specific, actionable recommendations:

1. Add `N` unit tests for `<module>` — currently 0%, logic is pure and easily testable
2. Replace flaky E2E test `<path>` with a faster integration test — the assertion does not need a browser
3. Add E2E smoke test for `<journey>` — highest P0 risk, currently zero browser-level coverage

## Step 5 — Suggested ratio

State the recommended ratio for this project specifically, with justification:

> For this project (risk profile: high E2E dependency on third-party payment API, logic-heavy cart calculations), recommend: 60% unit / 25% integration / 15% E2E.
