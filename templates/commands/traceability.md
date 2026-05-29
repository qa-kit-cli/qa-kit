---
command: qakit.traceability
description: Map requirements to test cases, test files, and CI jobs in a traceability matrix.
---

# /qakit.traceability

Build a traceability matrix.

Read `.qakit/memory/test-plan.md`, `.qakit/memory/qa-strategy.md`, and any requirements documentation, then produce a full traceability matrix.

## Output format

Save to `.qakit/memory/traceability-matrix.md`:

```markdown
# Traceability Matrix

| Req ID | Requirement | Risk | TC ID | Test Case | Test File | CI Job | Last Result | Notes |
|--------|-------------|------|-------|-----------|-----------|--------|-------------|-------|
| REQ-001 | User login | High | TC-001 | Login happy path | tests/e2e/login.spec.ts | e2e | ✅ Pass | |
| REQ-002 | Password reset | Medium | TC-005 | Reset via email | tests/e2e/auth.spec.ts | e2e | ⚠️ Flaky | Retry on CI |
| REQ-003 | 2FA enforcement | High | TC-010 | 2FA required | tests/e2e/auth.spec.ts | e2e | ❌ Missing | Not yet written |
```

## Columns

- **Req ID**: Requirement or user story identifier
- **Requirement**: Brief description of what must work
- **Risk**: High / Medium / Low (from qa-strategy.md)
- **TC ID**: Test case ID from test-plan.md
- **Test Case**: Name of the test
- **Test File**: Relative path to the test file
- **CI Job**: Which CI job runs this test
- **Last Result**: ✅ Pass / ❌ Fail / ⚠️ Flaky / 🔲 Missing
- **Notes**: Known issues, workarounds, or dependencies

## Rules

- Flag all requirements with no corresponding test case as gaps.
- Flag all test cases not mapped to any requirement as orphans.
- Highlight high-risk requirements with missing or flaky coverage.
- If a test file is specified, verify it exists in the repo.

$ARGUMENTS
