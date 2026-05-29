# Extension Development Guide

This guide walks through building a QA Kit extension from scratch.

## Prerequisites

- QA Kit CLI installed (`uv tool install qa-kit-cli` or `uv run qakit`)
- A project with QA Kit initialised (`qakit init`)

## Step 1: Create the Extension Directory

```
my-extension/
  extension.yml
```

You can put this directory anywhere: inside your project, in a shared monorepo, or in a separate repository.

## Step 2: Write the Manifest

Create `extension.yml`:

```yaml
id: my-extension
name: My Extension
version: 0.1.0
description: Runs a post-strategy validation script.

hooks:
  - after_strategy
  - after_testplan

commands:
  after_strategy: "python scripts/validate_strategy.py"
  after_testplan: "python scripts/validate_plan.py"
```

**Rules:**
- `id` must be unique, kebab-case
- Every event in `commands` must also appear in `hooks`
- Commands run in the project root directory (`cwd`)
- Use only events from the supported hook event list (see `RFC-EXTENSION-SYSTEM.md`)

## Step 3: Validate the Manifest

```bash
# Install it locally and check for errors
qakit extension add ./my-extension
qakit extension list
```

If your `extension.yml` contains an unsupported hook event, `add` will print an error and refuse to install.

## Step 4: Test the Hooks

Run a workflow that triggers the hooks you subscribed to:

```bash
qakit workflow run qakit
```

Your extension command will execute automatically after the corresponding step.

To test a single hook event without running a full workflow, you can manually invoke the shell command listed in `commands`:

```bash
python scripts/validate_strategy.py
```

## Step 5: Add Scripts

Store helper scripts in a `scripts/` subdirectory:

```
my-extension/
  extension.yml
  scripts/
    validate_strategy.py
    validate_plan.py
```

Reference them with relative paths in `extension.yml`. The working directory when hooks run is the project root, so use paths relative to the project root (e.g., `scripts/` inside the extension copy in `.qakit/extensions/<id>/scripts/`).

## Available Environment Variables

When a hook command runs, the following environment variables are set:

| Variable | Value |
|---|---|
| `QAKIT_DIR` | Absolute path to `.qakit/` |
| `QAKIT_PROJECT_ROOT` | Absolute path to the project root |
| `QAKIT_INTEGRATION` | Active integration key (e.g., `claude`, `copilot`) |

## Cross-Platform Notes

- On Windows, commands are run via `subprocess.call(command, shell=True)`, which invokes `cmd.exe`.
- Use Python scripts (not bash) if you need cross-platform compatibility.
- PowerShell scripts can be used with `pwsh -File scripts/validate.ps1`.

## Writing Tests for Your Extension

Test that your shell commands behave correctly before publishing:

```python
import subprocess, pathlib

def test_validate_strategy_exits_zero(tmp_path):
    # Create a minimal .qakit/memory/qa-strategy.md
    strategy = tmp_path / ".qakit" / "memory" / "qa-strategy.md"
    strategy.parent.mkdir(parents=True)
    strategy.write_text("# QA Strategy\n...")

    rc = subprocess.call(
        "python scripts/validate_strategy.py",
        shell=True,
        cwd=tmp_path,
    )
    assert rc == 0
```

## Example: Slack Notification Extension

```yaml
id: slack-notify
name: Slack Notifications
version: 0.1.0
description: Posts Slack messages after key QA milestones.

hooks:
  - after_testplan
  - after_ci_github_actions

commands:
  after_testplan: >
    [ -z "$SLACK_WEBHOOK_URL" ] && echo '[slack-notify] SLACK_WEBHOOK_URL not set' ||
    curl -s -X POST -H 'Content-type: application/json'
    --data '{"text":"Test plan updated — run /qakit.coverage to check gaps."}'
    "$SLACK_WEBHOOK_URL"
  after_ci_github_actions: >
    [ -z "$SLACK_WEBHOOK_URL" ] && echo '[slack-notify] SLACK_WEBHOOK_URL not set' ||
    curl -s -X POST -H 'Content-type: application/json'
    --data '{"text":"CI pipeline configured. Review the generated workflow file."}'
    "$SLACK_WEBHOOK_URL"
```

## Next Steps

- See `EXTENSION-API-REFERENCE.md` for the full manifest schema
- See `EXTENSION-PUBLISHING-GUIDE.md` to share your extension
- See `EXTENSION-USER-GUIDE.md` for how end users install extensions
