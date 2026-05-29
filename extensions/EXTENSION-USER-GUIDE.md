# Extension User Guide

Extensions add lifecycle hooks to QA Kit commands. When you run a workflow, enabled extensions execute shell commands automatically at key points — committing files, syncing with TestRail, posting to Slack, enforcing coverage gates, and so on.

## Installing an Extension

### From the bundled catalog

```bash
# List available bundled extensions
qakit extension list

# Install a bundled extension
qakit extension add git
qakit extension add coverage-gate
qakit extension add allure
qakit extension add testrail
qakit extension add jira
qakit extension add test-numbering
```

### From a local directory

```bash
qakit extension add ./path/to/my-extension
```

### From a remote archive

```bash
qakit extension add https://github.com/org/my-extension/releases/download/v1.0.0/extension.zip
```

## Managing Extensions

```bash
# List all installed extensions and their status
qakit extension list

# Disable an extension (keeps it installed, stops hooks from firing)
qakit extension disable git

# Re-enable a disabled extension
qakit extension enable git

# Remove an extension entirely
qakit extension remove git
```

## Bundled Extensions

| Extension | What it does |
|---|---|
| `git` | After `/qakit.strategy` and `/qakit.testplan`, commits the updated memory files with a standard commit message. |
| `coverage-gate` | After CI and Playwright commands, checks that coverage thresholds are defined in `test-policy.md` and warns if they are not. |
| `test-numbering` | After test-writing commands, scans the test files and lists any tests missing a `TC-NNN` traceability ID. |
| `allure` | After CI configuration commands, reminds you to add Allure report upload steps to the generated workflow. |
| `testrail` | After `testplan` and CI commands, syncs the test plan with your TestRail project (requires `TESTRAIL_URL` and `TESTRAIL_API_KEY`). |
| `jira` | After `/qakit.review.bugreport`, creates a Jira ticket from the bug report (requires `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN`). |

## Using Credentials with Extensions

Extensions that connect to external services read credentials from environment variables. Set them in your shell profile or CI environment:

```bash
# TestRail
export TESTRAIL_URL=https://yourorg.testrail.io
export TESTRAIL_API_KEY=your-api-key

# Jira
export JIRA_URL=https://yourorg.atlassian.net
export JIRA_USER=you@example.com
export JIRA_API_TOKEN=your-api-token
```

Alternatively, store tokens in the QA Kit token store:

```bash
qakit token set testrail
qakit token set jira
```

## How Hooks Work

When you run a workflow:

1. Before each command step, any `before_<command>` hooks from enabled extensions fire.
2. The command step runs (logs the dispatch).
3. If the command step succeeds, `after_<command>` hooks fire.
4. If a hook command fails (non-zero exit), a warning is printed, but the workflow continues.

## Troubleshooting

**Hook not firing:** Check that the extension is enabled (`qakit extension list`). Verify the event name in `extension.yml` matches the command being run.

**"Unsupported hook events" error on install:** The extension references an event name that QA Kit does not support. Check `RFC-EXTENSION-SYSTEM.md` for the list of valid events.

**Credential not found warning:** Set the required environment variable (e.g. `TESTRAIL_URL`) before running the workflow.
