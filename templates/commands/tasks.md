---
command: qakit.tasks
description: Generate a QA implementation task list from the active strategy and test plan.
---

# /qakit.tasks

Generate a QA implementation task list.

Read `.qakit/memory/qa-strategy.md` and `.qakit/memory/test-plan.md`, then generate a structured, actionable QA implementation task list.

## Output format

Save the task list to `.qakit/memory/test-tasks.md` using this structure:

```markdown
# QA Implementation Tasks

## Sprint / Milestone: [name]

### P0 — Blocking (must complete before release)
- [ ] TC-001: [Task description] — [owner] — [framework] — [est. hours]

### P1 — High Priority
- [ ] TC-010: [Task description] — [owner] — [framework] — [est. hours]

### P2 — Standard
- [ ] TC-020: [Task description] — [owner] — [framework] — [est. hours]

### P3 — Nice to Have
- [ ] TC-030: [Task description] — [owner] — [framework] — [est. hours]
```

## Rules

- Map each test case ID from test-plan.md to a concrete implementation task.
- Group by priority (P0–P3) based on risk and release criticality.
- Include the test framework (Playwright, Jest, Cypress, etc.) for each task.
- Estimate effort in hours where possible.
- Flag tasks that have dependencies or blockers.
- Note which tasks can run in parallel.

$ARGUMENTS
