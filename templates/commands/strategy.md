---
command: qakit.strategy
description: Generate a full QA strategy document for a feature or project.
---

# /qakit.strategy

Generate a complete QA strategy document and save it to `.qakit/memory/qa-strategy.md`.

## Context

**Input:** $ARGUMENTS
*(Paste feature spec, PRD, Jira ticket, or plain description. If left blank, analyse the current working directory — README, src/, and recent git diff.)*

Before writing, read:
- `.qakit/memory/test-policy.md` — honour coverage thresholds, approved frameworks, and environment matrix
- Any existing `.qakit/memory/qa-strategy.md` — update rather than replace if one exists

## What to produce

Write a complete `qa-strategy.md` using the sections below. Be concrete: name real user journeys, real risk areas, real acceptance criteria. Do not leave placeholder text.

---

## Feature Overview and Risk Classification

State what the feature does and classify its risk:
- **P0 — Critical path:** data loss, auth, payments, core CRUD
- **P1 — High:** primary user journeys, integrations
- **P2 — Medium:** secondary flows, edge cases
- **P3 — Low:** cosmetic, help text, low-traffic paths

## User Journeys to Test

List every distinct user journey as a numbered item. For each, state:
- Journey name
- Start state and end state
- Risk level (P0–P3)
- Whether it is independently testable

## Test Types Required

For each test type, state Yes/No and why:
| Type | Required | Justification |
|---|---|---|
| Unit | | |
| Integration | | |
| E2E | | |
| Visual regression | | |
| Accessibility (WCAG 2.1 AA) | | |
| API contract | | |
| Performance/load | | |

## Acceptance Criteria

Write each criterion in Given-When-Then format. Every criterion must be:
- Measurable (pass/fail deterministic)
- Mapped to at least one user journey above
- Achievable in the CI environment

## Data Requirements

- Test data needed (users, records, seed state)
- PII or sensitive data concerns and how to handle them
- Fixture strategy (static JSON, factory functions, or seeded DB)

## Environment Requirements

- Browsers and versions required (reference `test-policy.md` environment matrix)
- OS variants needed
- External services or mocks required (API keys, stubs)

## Edge Cases and Negative Scenarios

At minimum cover:
- Empty / null inputs
- Boundary values
- Concurrent access or race conditions
- Network failure / timeout paths
- Unauthorised access attempts

## Out of Scope

Explicitly list what will NOT be tested in this cycle and why.

## Needs Clarification

List up to three open questions that would change the test strategy if answered differently. Format: `[NEEDS CLARIFICATION] <question>`

---

**Save the completed document to `.qakit/memory/qa-strategy.md`.**
If `.qakit/memory/qa-strategy.md` already exists, update it in place — preserve any sections that remain valid.
