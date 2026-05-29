# QA Strategy

## Feature Overview and Risk Classification

**Feature:** <!-- e.g. "User Authentication — OAuth 2.0 + MFA" -->
**Risk Level:** <!-- High / Medium / Low -->
**Reason for Risk Classification:** <!-- e.g. "Handles PII and payment data; regression breaks checkout" -->
**Target Release:** <!-- e.g. "v2.4 — 2026-06-15" -->

## User Journeys to Test

List the independently testable journeys, ordered by business priority.

### P1 — Critical (must pass before release)

- **Journey 1:** <!-- e.g. "New user registers, verifies email, and logs in for the first time" -->
- **Journey 2:** <!-- e.g. "Existing user resets forgotten password via email link" -->

### P2 — Important (should pass before release)

- **Journey 3:** <!-- e.g. "User enables MFA and recovers access using backup code" -->

### P3 — Nice-to-have (track but non-blocking)

- **Journey 4:** <!-- e.g. "User changes email address while logged in" -->

## Test Types Required

| Type | Required | Rationale |
|---|---|---|
| Unit | Yes | Business logic in auth service, token validation, password hashing |
| Integration | Yes | OAuth provider handshake, session store, email delivery |
| E2E | Yes | Full login/logout flows in supported browsers |
| API Contract | Yes | Auth endpoints: POST /login, POST /refresh, DELETE /session |
| Accessibility | Yes | Login form must meet WCAG 2.1 AA |
| Visual Regression | No | Low visual change risk |
| Performance / Load | Optional | Target: ≤ 200 ms p95 login response under 500 concurrent users |

## Acceptance Criteria

Write each criterion in Given-When-Then format with a measurable assertion.

```
Given a registered user with valid credentials
When they submit the login form
Then they are redirected to the dashboard within 2 seconds
 And a session cookie is set with Secure + HttpOnly + SameSite=Strict flags

Given a user who enters an incorrect password 5 times
When they attempt a 6th login
Then the account is temporarily locked for 15 minutes
 And a lock notification email is sent within 30 seconds
```

## Data Requirements

- **Test accounts:** At least 3 fixture users: `verified@example.com`, `unverified@example.com`, `locked@example.com`
- **PII handling:** No real email addresses or phone numbers in test fixtures; use `@example.com` domain
- **Secrets management:** OAuth client credentials stored in `QAKIT_TOKEN_OAUTH_CLIENT_ID` / `QAKIT_TOKEN_OAUTH_CLIENT_SECRET` — never committed
- **Seed script:** `scripts/seed-auth-fixtures.ts` populates the test database before the suite runs

## Environment Requirements

| Environment | Purpose | Notes |
|---|---|---|
| `local` | Developer smoke test | Mock OAuth provider (e.g. `mock-oauth2-server`) |
| `ci` | Full suite on every PR | Ephemeral DB + real OAuth provider test tenant |
| `staging` | Release gate | Mirrors production data shape; no real PII |

**Browsers (E2E):** Chromium, Firefox, WebKit (via Playwright)
**Node version:** 20 LTS
**OS matrix:** ubuntu-latest (CI), macOS 14 (local developer default)

## Edge Cases and Negative Scenarios

- Login with SQL-injection payload in email field → must return 400, not 500
- Session token replay after logout → must return 401
- OAuth callback with tampered `state` parameter → must reject and log security event
- Simultaneous login from two devices → both sessions valid (or last-wins, per policy)
- Password reset link used twice → second attempt must return 410 Gone

## Out of Scope

- Social login providers other than Google and GitHub (v0.1 scope)
- SMS-based MFA (planned for v2.5)
- Admin impersonation flows (covered by separate admin test plan)
- Load testing beyond 500 concurrent users (handled by dedicated performance team)

## [NEEDS CLARIFICATION]

1. <!-- e.g. "What is the expected behaviour when the OAuth provider returns a 429 rate-limit response? Should we retry, or show the user an error immediately?" -->
2. <!-- e.g. "Is account lockout shared across devices or per-device?" -->
3. <!-- e.g. "Should the E2E suite run against the staging OAuth tenant or a dedicated test tenant?" -->
