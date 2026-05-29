---
command: qakit.clarify
description: Identify and resolve ambiguities in a QA strategy or test plan.
---

# /qakit.clarify

Identify every ambiguity in the active QA strategy or test plan and either resolve it or surface it as a targeted question.

## Context

**Input:** $ARGUMENTS
*(Optional: focus area, e.g. "clarify the checkout flow data requirements" or "resolve TC-014 flakiness root cause". Defaults to full strategy + plan review.)*

Read:
- `.qakit/memory/qa-strategy.md`
- `.qakit/memory/test-plan.md`
- `.qakit/memory/test-policy.md`

Also read the source files for the relevant feature area to spot gaps between the written spec and the actual implementation.

## Step 1 — Ambiguity scan

Look for these types of ambiguity:

**Scope ambiguities** — "test the checkout flow" without specifying which payment methods, error states, or currency variants.

**Criterion ambiguities** — acceptance criteria that are not binary (e.g., "the page should load quickly" — what is the threshold?).

**Data ambiguities** — fixture or seed data requirements that are underspecified (e.g., "a user with an account" — which role? which plan? any specific state?).

**Environment ambiguities** — references to "production-like" without stating browser, OS, or service versions.

**Ownership ambiguities** — steps in a test that depend on external teams, services, or APIs that have no stub or contract defined.

**`[NEEDS CLARIFICATION]` markers** — explicit open questions left in strategy or plan docs.

## Step 2 — Resolution attempt

For each ambiguity, try to resolve it from available information:
- Source code, config files, `package.json`, API schemas, OpenAPI specs
- Existing tests that already make an implicit choice
- `test-policy.md` defaults

Mark each resolved or unresolved:
- ✅ **Resolved** — state the resolution and its source
- ❓ **Needs answer** — cannot resolve without human input

## Step 3 — Questions for the team

For every unresolved ambiguity, write a precise, answerable question:

```
Q1 [Data] What user roles must be tested in the checkout flow?
  Context: qa-strategy.md line 34 says "a logged-in user" without role specification.
  Impact: determines whether we need 3 fixture users or 1; affects TC-007 through TC-012.
  Options: (a) admin + regular user, (b) regular user only, (c) all roles
```

Limit to the most impactful questions. Do not ask about things that can be inferred.

## Step 4 — Updated documents

After resolving what can be resolved:
- Update `.qakit/memory/qa-strategy.md` to replace each `[NEEDS CLARIFICATION]` marker with the resolved answer or a clearer open question
- Update `.qakit/memory/test-plan.md` if any data model or environment sections are affected

Print a summary of changes made and questions still open.
