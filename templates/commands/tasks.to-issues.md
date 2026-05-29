---
command: qakit.tasks.to-issues
description: Convert QA task plans into GitHub issue-ready drafts grouped by category.
---

# /qakit.tasks.to-issues

Generate GitHub issue drafts from QA tasks.

Read:
- `.qakit/memory/test-plan.md`
- `.qakit/memory/test-tasks.md` (from `/qakit.tasks`)

Then group tasks into these categories:
- test writing
- CI setup
- regression
- review

For each task, generate an issue draft with:
- Title: `[QA] <task description>`
- Labels: `qa`, `testing`, and a framework label when applicable
- Body:
  - Acceptance criteria from `test-plan.md`
  - Definition of done
  - Links to relevant `.qakit/memory/` files

Output a summary table:

| Task | Issue Title | Labels | Assignee |
|---|---|---|---|
| ... | ... | ... | |

If `GITHUB_TOKEN` is set, append a `gh` CLI block that can bulk-create the issues.

Use `$ARGUMENTS` for optional sprint/milestone filtering.

$ARGUMENTS
