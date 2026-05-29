# Bug Report

- **ID:** BUG-<!-- NNN -->
- **Severity:** <!-- P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low) -->
- **Priority:** <!-- Blocker | High | Medium | Low -->
- **Status:** <!-- Open | In Progress | Fixed | Verified | Closed | Won't Fix -->
- **Reporter:** <!-- @github-handle -->
- **Assignee:** <!-- @github-handle -->
- **Date Found:** <!-- YYYY-MM-DD -->
- **Target Fix Version:** <!-- e.g. v2.4.1 -->
- **Linked Test Cases:** <!-- TC-003, TC-016 -->
- **Linked PR / Commit:** <!-- #123 or sha -->

---

## Environment

| Item | Value |
|---|---|
| Application version | <!-- e.g. v2.4.0-rc1 --> |
| Browser / Client | <!-- e.g. Chrome 124 / iOS Safari 17 / curl 8.4 --> |
| OS | <!-- e.g. macOS 14.4 / Ubuntu 22.04 / Windows 11 --> |
| Test environment | <!-- local / ci / staging / production --> |
| Relevant feature flags | <!-- e.g. `AUTH_MFA_ENABLED=true` --> |

---

## Summary

<!-- One sentence: what broke and in what context. -->
<!-- Example: "Submitting the login form with a valid email and correct password returns HTTP 500 when the Redis session store is temporarily unreachable." -->

---

## Steps to Reproduce

1. <!-- e.g. Navigate to `/login` -->
2. <!-- e.g. Enter `verified@example.com` and `Test1234!` -->
3. <!-- e.g. Click "Sign in" -->
4. <!-- e.g. Observe the response -->

**Reproducibility:** <!-- Always / Intermittent (N/M times) / Once -->

---

## Expected Result

<!-- What should happen according to the spec or acceptance criteria. -->
<!-- Example: "User is redirected to `/dashboard` with a 302 response and a valid session cookie." -->

---

## Actual Result

<!-- What actually happens. Include status codes, error messages, and stack traces. -->
<!-- Example: "HTTP 500 Internal Server Error. Console shows: `RedisConnectionError: connect ECONNREFUSED 127.0.0.1:6379`" -->

---

## Evidence

- **Screenshot / Recording:** <!-- Attach or link -->
- **HAR file:** <!-- Attach if network issue -->
- **Server logs:** <!-- Paste relevant lines or link to log artefact -->
- **Playwright trace:** <!-- Link to `.zip` artefact from failed CI run -->

```
<!-- Paste relevant log lines here -->
```

---

## Root Cause Hypothesis

<!-- Initial diagnosis. Example: "The auth controller does not handle Redis connection errors gracefully — the session.create() call throws an unhandled exception instead of falling back to a degraded-mode response." -->

---

## Suggested Fix

<!-- If known. Example: "Wrap `session.create()` in a try/catch; return a 503 with `Retry-After: 5` header instead of propagating the Redis error." -->
