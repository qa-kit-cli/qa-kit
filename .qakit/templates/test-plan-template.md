# Test Plan

## Summary

**Feature / Initiative:** <!-- e.g. "User Authentication — OAuth 2.0 + MFA" -->
**Version:** <!-- e.g. "v2.4" -->
**Status:** Draft | In Review | Approved | Active | Archived
**Owner:** <!-- e.g. "@qa-engineer" -->
**Last Updated:** <!-- YYYY-MM-DD -->

**Objectives:**
- Verify all P1 user journeys pass on Chromium, Firefox, and WebKit before release
- Achieve ≥ 80% unit coverage on the auth service module
- Zero P0/P1 defects open at release gate

**Exit Criteria:**
- All TC-P1 test cases pass across the full browser matrix
- Code coverage ≥ 80% unit, ≥ 60% integration
- No open P0 or P1 defects
- Flakiness rate < 2% over the last 5 CI runs

## Technical Context

| Item | Value |
|---|---|
| Framework (E2E) | Playwright 1.44 + TypeScript 5.4 |
| Framework (Unit) | Jest 29 + ts-jest |
| CI Environment | GitHub Actions — `ubuntu-22.04` |
| Node version | 20.x LTS |
| Browser matrix | Chromium, Firefox, WebKit |
| Test data strategy | Fixture files + factory functions (`tests/fixtures/`) |
| Reporting | JUnit XML (CI) + HTML report (`playwright-report/`) |

## Policy Check

> Read `test-policy.md` before finalising this section. Flag any deviations.

- **Coverage thresholds:** Unit ≥ 80%, Integration ≥ 60% — **ALIGNED** ✓
- **Approved frameworks:** Playwright (E2E), Jest (Unit) — **ALIGNED** ✓
- **Flakiness policy:** Retry count ≤ 2; quarantine threshold = 3 consecutive failures — **ALIGNED** ✓
- **Test ID scheme:** TC-NNN assigned per test case — **ALIGNED** ✓

## Test Architecture

**Target pyramid ratio:**

| Layer | Target % | Count (est.) | Notes |
|---|---|---|---|
| Unit | 60% | ~45 tests | Auth service, token helpers, validators |
| Integration | 25% | ~19 tests | OAuth handshake, DB session store, email service |
| E2E | 15% | ~11 tests | Critical P1 and P2 journeys × browser matrix |

## Test Suite Layout

```
tests/
├── unit/
│   ├── auth.service.test.ts      # Token generation, password hashing, lockout logic
│   └── validators.test.ts        # Email format, password strength rules
├── integration/
│   ├── oauth.flow.test.ts        # OAuth provider callback + state validation
│   └── session.store.test.ts     # Session create/read/delete against real Redis
└── e2e/
    ├── login.spec.ts             # TC-001 … TC-004  Happy-path login flows
    ├── password-reset.spec.ts    # TC-005 … TC-007  Password reset journey
    └── mfa.spec.ts               # TC-008 … TC-011  MFA enrol + recovery
```

**Naming conventions:**
- Unit/Integration: `*.test.ts`
- E2E: `*.spec.ts`
- Fixtures: `tests/fixtures/<name>.ts` — factory functions, no hardcoded IDs

## Environment Matrix

| Suite | Local | CI (PR) | Staging (Release gate) |
|---|---|---|---|
| Unit | ✓ | ✓ | — |
| Integration | ✓ (Docker Compose) | ✓ (service containers) | — |
| E2E — Chromium | ✓ | ✓ | ✓ |
| E2E — Firefox | — | ✓ | ✓ |
| E2E — WebKit | — | ✓ | ✓ |

## Data Model

**Fixtures (`tests/fixtures/users.ts`):**
```typescript
export const verifiedUser = { email: "verified@example.com", password: "Test1234!" };
export const unverifiedUser = { email: "unverified@example.com", password: "Test1234!" };
export const lockedUser = { email: "locked@example.com", password: "Test1234!" };
```

**Factory functions:** `createUser(overrides?)`, `createSession(userId)`, `createOAuthState()`

**Seed script:** `npm run seed:test` — calls `scripts/seed-auth-fixtures.ts`, idempotent, runs before E2E suite.

**PII policy:** All test data uses `@example.com` domain. No real names, phone numbers, or addresses in fixtures.

## CI/CD Integration

| Stage | Trigger | Tests run | Gate |
|---|---|---|---|
| PR check | Every push to PR branch | Unit + Integration + E2E (Chromium only) | Required to merge |
| Main branch | Merge to `main` | Full matrix (all browsers) | Required |
| Release gate | Tag `v*` | Full matrix + staging smoke test | Required to publish |

**Artefacts retained:** JUnit XML (30 days), HTML report (30 days), Playwright traces on failure (7 days).
