# /qakit.review.pr

Review a pull request from a QA perspective: coverage delta, missing edge cases, risk areas.

## Description

Reads the PR diff and evaluates it against the QA context in `.qakit/memory/`: risk classification of changed areas, test coverage delta (source files changed vs. test changes present), missing test scenarios, test quality (locators, flakiness patterns, TC-NNN IDs), coverage gate prediction, and regression risk.

Produces a structured verdict with actionable checklist items.

## Usage

```
/qakit.review.pr <PR reference>
```

## Arguments

- PR number, branch name, or pasted diff
- Examples: `#142`, `feature/checkout-refactor`

## Reads from memory

- `.qakit/memory/test-policy.md` — coverage thresholds and CI gates
- `.qakit/memory/qa-strategy.md` — risk levels for affected feature areas
- `.qakit/memory/test-plan.md` — TC-NNN tests that should cover these changes

## Produces

Inline review with sections:
1. **Risk assessment** — risk level of changed code areas
2. **Coverage delta table** — every changed source file with pass/fail on test coverage
3. **Missing scenarios** — uncovered error paths, edge cases, race conditions
4. **Test quality checklist** — locators, waits, TC-NNN IDs, assertion specificity
5. **Coverage gate prediction** — PASS / FAIL / AT RISK
6. **Verdict** — Approve / Request changes, with specific action items

## Example

```
/qakit.review.pr #142
```

## Related commands

- `/qakit.write.playwright` — write the missing tests identified in the review
- `/qakit.maintain.flaky` — fix flaky patterns flagged in the review
- `/qakit.review.bugreport` — create a bug report for any defects found during review
