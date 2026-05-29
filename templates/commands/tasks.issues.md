---
command: qakit.tasks.issues
description: Convert QA task list to GitHub Issues or Jira tickets
---

# /qakit.tasks.issues

Convert the QA implementation task list into GitHub Issues or Jira tickets,
applying standard QA labels and populating the traceability matrix with
created issue URLs.

## Context files to read

Before starting, read these files:

- `.qakit/memory/test-tasks.md` — source task list with TC-IDs and priority tiers
- `.qakit/memory/test-policy.md` — label conventions, milestone mapping, and governance rules
- `.qakit/memory/qa-strategy.md` — risk context to include in issue descriptions

## Arguments

`$ARGUMENTS` may include any combination of:

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--target` | `github`, `jira`, `both` | `github` | Issue tracker to create tickets in |
| `--dry-run` | flag | false | Print what would be created without actually creating |
| `--label` | string | — | Additional label(s) to apply to every issue |
| `--milestone` | string | — | Milestone or sprint to assign every issue |

---

## Step 1 — Parse test-tasks.md

Read `.qakit/memory/test-tasks.md` and extract every task entry.

Each task line follows this format:
```
- [ ] TC-NNN: Task description — owner — framework — est. hours
```

Also parse optional journey tags such as `[Journey-1]` and phase headings
(`P0 — Blocking`, `P1 — High Priority`, `P2 — Standard`, `P3 — Nice to Have`).

Group tasks into four priority tiers:

| Tier | Label | Description |
|------|-------|-------------|
| P0 | Blocking | Must complete before release |
| P1 | High Priority | Must complete for quality bar |
| P2 | Standard | Normal sprint work |
| P3 | Nice to Have | Defer when pressed for time |

For each task extract:
- `tc_id`: e.g. `TC-001`
- `priority`: P0, P1, P2, or P3
- `description`: the task description text
- `owner`: assigned engineer (if present)
- `framework`: Playwright, Jest, Cypress, etc. (if present)
- `estimate`: hours estimate (if present)

---

## Step 2 — Determine target

Parse `--target` from `$ARGUMENTS`. Default to `github`.

If `--target both`, create issues in both GitHub and Jira sequentially.

---

## Step 3a — GitHub issue creation

### Prerequisites check

Verify `gh` CLI is installed and authenticated:
```bash
gh auth status
```

If `gh` is not available or not authenticated, print an error and stop:
```
Error: GitHub CLI (gh) is required. Install from https://cli.github.com/
       then run: gh auth login
```

### Issue format

For each task, compose the following:

**Title:**
```
[QA][P{priority}][{tc_id}] {description}
```

Example: `[QA][P0][TC-001] Write login happy-path Playwright test`

**Body:**
```markdown
## QA Task: {tc_id}

**Priority:** {priority} — {priority_description}
**Framework:** {framework}
**Estimate:** {estimate}
**Owner:** {owner}

## Description

{description}

Derived from `.qakit/memory/test-tasks.md`. Context in `.qakit/memory/qa-strategy.md`.

## Acceptance Criteria

- [ ] Test case {tc_id} is implemented and passing in CI
- [ ] Code coverage meets or exceeds the threshold in `test-policy.md`
- [ ] Test is tagged with canonical ID `{tc_id}` in the test file
- [ ] Added to the regression suite in `.qakit/memory/regression-suite.md`
- [ ] Traceability matrix updated in `.qakit/memory/traceability-matrix.md`

## Labels

`qa` · `testing` · `{priority_lower}` · `{framework_lower}` (if applicable)
```

**Labels to apply:** `qa`, `testing`, `p0`/`p1`/`p2`/`p3` (lowercase priority).
Apply additional labels from `--label` if provided.

### Dry-run mode

If `--dry-run` is set, print each issue that *would* be created but do not
invoke `gh issue create`. Prefix output with `[DRY RUN]`.

### Creation command

For each task:
```bash
gh issue create \
  --title "[QA][P{priority}][{tc_id}] {description}" \
  --body "{body}" \
  --label "qa" \
  --label "testing" \
  --label "{priority_lower}"
```

If `--milestone` is provided, append `--milestone "{milestone}"`.

### Summary table

After creating all issues, print:

| TC ID | Title | Issue URL | Status |
|-------|-------|-----------|--------|
| TC-001 | [QA][P0][TC-001] … | https://github.com/… | Created |
| TC-002 | [QA][P1][TC-002] … | — | Dry-run |

---

## Step 3b — Jira ticket creation

### Prerequisites check

Verify `JIRA_URL` and `JIRA_API_TOKEN` environment variables are set:
```bash
echo $JIRA_URL        # e.g. https://myorg.atlassian.net
echo $JIRA_API_TOKEN  # Atlassian API token
```

If either is missing, print an error and stop:
```
Error: Jira integration requires JIRA_URL and JIRA_API_TOKEN environment variables.
       Set them and retry.
```

### Priority mapping

Map QA priority tiers to Jira issue types:

| QA Priority | Jira Priority |
|-------------|---------------|
| P0 | Blocker |
| P1 | Critical |
| P2 | Major |
| P3 | Minor |

### Ticket creation

Use the Jira REST API v3 to create each ticket:
```bash
curl -X POST "$JIRA_URL/rest/api/3/issue" \
  -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": { "key": "QA" },
      "summary": "[{tc_id}] {description}",
      "issuetype": { "name": "Task" },
      "priority": { "name": "{jira_priority}" },
      "labels": ["qa", "testing", "{priority_lower}"]
    }
  }'
```

---

## Step 4 — Update traceability matrix

After issues are created, append the issue URLs to
`.qakit/memory/traceability-matrix.md`.

Find the row for each `TC-NNN` and add or update an **Issue** column:

| TC ID | Requirement | … | Issue |
|-------|-------------|---|-------|
| TC-001 | … | … | https://github.com/owner/repo/issues/42 |

If the traceability matrix does not yet have an Issue column, add one.
If a task was dry-run, write `(dry-run)` in the Issue column.

---

## Final output

After processing all tasks, print a summary:

```
Created {N} issues from {total} QA tasks.
  GitHub: {github_count} issues
  Jira:   {jira_count} tickets
  Dry-run: {dry_run_count} skipped
```

$ARGUMENTS
