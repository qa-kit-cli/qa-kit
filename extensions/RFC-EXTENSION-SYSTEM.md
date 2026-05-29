# RFC: QA Kit Extension System

## Overview

Extensions allow third-party tools and CI integrations to hook into the QA Kit command lifecycle. An extension declares which command lifecycle events it cares about and provides shell commands to execute at those points.

## Motivation

QA Kit slash commands are designed to be generic — they don't know whether your project uses Allure, TestRail, Jira, or another tool. Extensions bridge that gap: they run automatically after commands complete and can perform reporting, validation, or synchronisation tasks without the user needing to remember to run them manually.

## Extension Directory Layout

```
my-extension/
  extension.yml         # Manifest (required)
  scripts/              # Optional helper scripts referenced in commands
  README.md             # Optional documentation
```

## Manifest: extension.yml

```yaml
id: my-extension               # Unique identifier, kebab-case
name: My Extension             # Human-readable display name
version: 0.1.0                 # Semantic version
description: What this does.   # One-line description

hooks:
  - after_strategy             # Events to subscribe to (see Hook Events below)
  - after_testplan

commands:
  after_strategy: "echo '[my-extension] strategy updated'"
  after_testplan: "python scripts/sync.py $QAKIT_DIR"
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique kebab-case identifier |
| `name` | string | Yes | Display name shown in `qakit extension list` |
| `version` | string | Yes | SemVer string |
| `description` | string | No | One-line description |
| `hooks` | list[string] | No | Lifecycle events to subscribe to |
| `commands` | map[string, string] | No | Shell command to run for each hook event |

Only hook events listed in `hooks` can appear as keys in `commands`. The executor validates this and raises an error if an unknown event is used.

## Hook Events

Hook events follow the naming convention `before_<action>` and `after_<action>`. Events are always paired — every `before_X` has a corresponding `after_X`.

### Current events

| Event pair | Triggered by |
|---|---|
| `before_strategy` / `after_strategy` | `/qakit.strategy` |
| `before_testplan` / `after_testplan` | `/qakit.testplan` |
| `before_coverage` / `after_coverage` | `/qakit.coverage` |
| `before_gaps` / `after_gaps` | `/qakit.gaps` |
| `before_policy` / `after_policy` | `/qakit.policy` |
| `before_write_playwright` / `after_write_playwright` | `/qakit.write.playwright` |
| `before_write_cypress` / `after_write_cypress` | `/qakit.write.cypress` |
| `before_write_jest` / `after_write_jest` | `/qakit.write.jest` |
| `before_write_vitest` / `after_write_vitest` | `/qakit.write.vitest` |
| `before_write_pom` / `after_write_pom` | `/qakit.write.pom` |
| `before_ci_github_actions` / `after_ci_github_actions` | `/qakit.ci.github-actions` |
| `before_ci_jenkins` / `after_ci_jenkins` | `/qakit.ci.jenkins` |
| `before_maintain_flaky` / `after_maintain_flaky` | `/qakit.maintain.flaky` |
| `before_review_pr` / `after_review_pr` | `/qakit.review.pr` |
| `before_review_bugreport` / `after_review_bugreport` | `/qakit.review.bugreport` |

Hook events that fail (non-zero exit code) are recorded but do not abort the workflow.

## Execution Model

When a workflow command step runs:

1. `WorkflowEngine` calls `HookExecutor.execute(active_manifests, "before_<prefix>")` before the command step.
2. The command step executes (logs the command, dispatches to the AI agent).
3. If the command step succeeded, `HookExecutor.execute(active_manifests, "after_<prefix>")` is called.
4. If the command step failed, the `after_*` hook is skipped and the workflow halts.

Hooks from all active extensions are called in order. Each hook runs as a shell command in the project root directory.

## Extension Registry

Extensions are resolved from three sources (checked in order):

1. **Absolute path** — if the ref is an existing directory path, use it directly.
2. **Bundled** — `qa_kit_cli/core_pack/extensions/<id>/`
3. **Local** — `.qakit/extensions/<id>/`
4. **Remote** — HTTPS URL to a `.zip` archive containing `extension.yml`

## Bundled Extensions

QA Kit ships with the following extensions:

| ID | Purpose |
|---|---|
| `git` | Commits QA memory files after strategy/testplan commands |
| `coverage-gate` | Warns if coverage thresholds are missing from test-policy.md |
| `test-numbering` | Detects tests missing TC-NNN traceability IDs |
| `allure` | Reminds to add Allure report upload steps to CI workflows |
| `testrail` | Syncs test plans and results with TestRail |
| `jira` | Creates Jira defect tickets from bug report outputs |

## Security Considerations

Extension commands execute arbitrary shell code in the project directory. Users should only install extensions from trusted sources. Bundled extensions are reviewed as part of the QA Kit release process. Remote extensions should be reviewed before installation.
