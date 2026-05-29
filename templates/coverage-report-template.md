# Coverage Report

**Generated:** <!-- YYYY-MM-DD HH:MM UTC -->  
**Feature / Initiative:** <!-- e.g. "User Authentication v2.4" -->  
**Test plan reference:** `.qakit/memory/test-plan.md`  
**Policy reference:** `.qakit/memory/test-policy.md`

---

## Requirement to Test Mapping

| Requirement / Acceptance Criterion | TC-IDs | Status | Notes |
|---|---|---|---|
| Successful login redirects to dashboard within 2 seconds | TC-001 | ✅ Covered | |
| Login form validates empty fields with inline errors | TC-002 | ✅ Covered | |
| Wrong password shows error without redirect | TC-003 | ✅ Covered | |
| Session cookie has correct security flags | TC-004 | ✅ Covered | |
| Password reset email sent for registered address | TC-005 | ✅ Covered | |
| Reset link is single-use | TC-006 | ✅ Covered | |
| New password enforces strength rules | TC-007 | ✅ Covered | |
| Account locks after 5 failed attempts | TC-014 | ✅ Covered | Unit test only — no E2E equivalent |
| OAuth callback rejects tampered state | TC-016 | ✅ Covered | Integration test |
| <!-- Requirement from spec --> | — | ❌ **GAP** | No test case exists |

---

## Missing Coverage

The following requirements or edge cases have no corresponding test case:

| # | Missing area | Priority | Suggested TC-ID | Action |
|---|---|---|---|---|
| 1 | <!-- e.g. "Rate limiting on /login endpoint (429 response)" --> | P1 | TC-018 | Add integration test |
| 2 | <!-- e.g. "Session expiry after 24 hours of inactivity" --> | P2 | TC-019 | Add E2E test with time mock |
| 3 | <!-- e.g. "Accessibility: login form keyboard navigation" --> | P2 | TC-020 | Add axe-core scan + tab-order test |

**Total gaps:** <!-- N -->  
**P1 gaps:** <!-- N --> (must be resolved before release)  
**P2 gaps:** <!-- N --> (should be resolved before release)

---

## Pyramid Ratio

| Layer | Target | Actual | Status |
|---|---|---|---|
| Unit | 60% | <!-- N% --> | <!-- ✅ / ⚠️ Below target / ❌ Missing --> |
| Integration | 25% | <!-- N% --> | <!-- ✅ / ⚠️ / ❌ --> |
| E2E | 15% | <!-- N% --> | <!-- ✅ / ⚠️ / ❌ --> |

**Total test cases:** <!-- N -->  
**Jest coverage (lines):** <!-- N% -->  — threshold: ≥ 80%  
**Jest coverage (branches):** <!-- N% --> — threshold: ≥ 70%

---

## Recommendations

1. **[P1] Add missing test cases** — See "Missing Coverage" table above. Run `qakit.write.playwright` or `qakit.write.jest` for each gap.
2. <!-- e.g. "[P2] Increase integration test count — currently below 25% of total suite. Consider extracting DB-layer tests from E2E flows." -->
3. <!-- e.g. "[P3] Consolidate duplicate fixture setup — 4 test files repeat the same `createUser()` boilerplate; move to `beforeAll` in a shared fixture." -->
