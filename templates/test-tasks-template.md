# Test Tasks

Task format: `[TC-NNN] [P?] [Journey-N] Description — path/to/test.spec.ts`

---

## Phase 1: Setup

- [ ] Initialise Playwright config (`playwright.config.ts`) with browser matrix, base URL, and reporter — `playwright.config.ts`
- [ ] Add Jest config (`jest.config.ts`) with coverage thresholds and ts-jest transform — `jest.config.ts`
- [ ] Create `tests/fixtures/` directory with base factory functions — `tests/fixtures/index.ts`
- [ ] Add CI skeleton (GitHub Actions workflow stub) — `.github/workflows/tests.yml`
- [ ] Configure `package.json` test scripts: `test:unit`, `test:integration`, `test:e2e`, `test:ci`

## Phase 2: Foundation

- [ ] Implement `createUser(overrides?)` factory with `@example.com` domain guard — `tests/fixtures/users.ts`
- [ ] Implement `createSession(userId)` factory — `tests/fixtures/sessions.ts`
- [ ] Implement `LoginPage` POM with `goto()`, `fillCredentials()`, `submit()`, `expectError()` — `tests/pages/LoginPage.ts`
- [ ] Implement `PasswordResetPage` POM — `tests/pages/PasswordResetPage.ts`
- [ ] Add `auth` helper: `loginAs(page, user)` reusable fixture — `tests/helpers/auth.ts`
- [ ] Add seed script (`scripts/seed-auth-fixtures.ts`) — idempotent, runs before E2E suite

## Phase 3: Test Suites per User Journey

### Journey 1 — New user registration and first login (P1)

- [ ] `[TC-001] [P1] [Journey-1] Successful login with valid credentials redirects to dashboard — tests/e2e/login.spec.ts`
- [ ] `[TC-002] [P1] [Journey-1] Login form rejects empty email and empty password with inline errors — tests/e2e/login.spec.ts`
- [ ] `[TC-003] [P1] [Journey-1] Login with wrong password shows error, does not redirect — tests/e2e/login.spec.ts`
- [ ] `[TC-004] [P1] [Journey-1] Session cookie has Secure + HttpOnly + SameSite=Strict flags — tests/e2e/login.spec.ts`

### Journey 2 — Password reset (P1)

- [ ] `[TC-005] [P1] [Journey-2] Password reset email is sent for registered address — tests/e2e/password-reset.spec.ts`
- [ ] `[TC-006] [P1] [Journey-2] Password reset link is single-use; second visit returns 410 — tests/e2e/password-reset.spec.ts`
- [ ] `[TC-007] [P1] [Journey-2] New password must meet strength requirements (8+ chars, 1 number) — tests/e2e/password-reset.spec.ts`

### Journey 3 — MFA enrolment and recovery (P2)

- [ ] `[TC-008] [P2] [Journey-3] User can enable TOTP MFA from account settings — tests/e2e/mfa.spec.ts`
- [ ] `[TC-009] [P2] [Journey-3] MFA prompt appears on subsequent login — tests/e2e/mfa.spec.ts`
- [ ] `[TC-010] [P2] [Journey-3] Backup code allows login when TOTP device is unavailable — tests/e2e/mfa.spec.ts`
- [ ] `[TC-011] [P2] [Journey-3] Used backup code is invalidated; remaining count decrements — tests/e2e/mfa.spec.ts`

### Unit — Auth service (P1)

- [ ] `[TC-012] [P1] [Unit] generateToken() returns a signed JWT with correct exp claim — tests/unit/auth.service.test.ts`
- [ ] `[TC-013] [P1] [Unit] hashPassword() output passes bcrypt.compare() — tests/unit/auth.service.test.ts`
- [ ] `[TC-014] [P1] [Unit] Account locks after 5 failed attempts within 10 minutes — tests/unit/auth.service.test.ts`

### Integration — OAuth and session store (P1)

- [ ] `[TC-015] [P1] [Integration] OAuth callback with valid code and state creates a session — tests/integration/oauth.flow.test.ts`
- [ ] `[TC-016] [P1] [Integration] OAuth callback with tampered state parameter returns 400 — tests/integration/oauth.flow.test.ts`
- [ ] `[TC-017] [P1] [Integration] Session store roundtrip: create → read → delete — tests/integration/session.store.test.ts`

## Phase N: Polish

- [ ] Wire coverage report to CI: `jest --coverage` output to `coverage/lcov.info`; fail if thresholds missed
- [ ] Add Playwright HTML report artefact upload step to CI workflow
- [ ] Add test coverage badge to `README.md` — `<!-- coverage badge -->`
- [ ] Establish flakiness baseline: run full suite 5 times in CI and document any intermittent failures
- [ ] Run `qakit.coverage` to confirm requirement → TC mapping is complete and no gaps remain
