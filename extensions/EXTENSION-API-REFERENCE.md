# Extension API Reference

## extension.yml Schema

```yaml
id: string             # Required. Unique kebab-case identifier.
name: string           # Required. Human-readable display name.
version: string        # Required. Semantic version (e.g. "0.2.0").
description: string    # Optional. One-line description.

hooks:                 # Optional. List of lifecycle events this extension subscribes to.
  - <event_name>       # Must be one of the supported hook events listed below.

commands:              # Optional. Map of event name → shell command to execute.
  <event_name>: "shell command string"
```

**Constraint:** Every key in `commands` must appear in `hooks`. The loader rejects manifests with undeclared hook events.

---

## Supported Hook Events

All events follow the pattern `before_<action>` or `after_<action>`.

| Event | Lifecycle point |
|---|---|
| `before_strategy` | Before `/qakit.strategy` is dispatched |
| `after_strategy` | After `/qakit.strategy` succeeds |
| `before_testplan` | Before `/qakit.testplan` |
| `after_testplan` | After `/qakit.testplan` succeeds |
| `before_coverage` | Before `/qakit.coverage` |
| `after_coverage` | After `/qakit.coverage` succeeds |
| `before_gaps` | Before `/qakit.gaps` |
| `after_gaps` | After `/qakit.gaps` succeeds |
| `before_policy` | Before `/qakit.policy` |
| `after_policy` | After `/qakit.policy` succeeds |
| `before_write_playwright` | Before `/qakit.write.playwright` |
| `after_write_playwright` | After `/qakit.write.playwright` succeeds |
| `before_write_cypress` | Before `/qakit.write.cypress` |
| `after_write_cypress` | After `/qakit.write.cypress` succeeds |
| `before_write_jest` | Before `/qakit.write.jest` |
| `after_write_jest` | After `/qakit.write.jest` succeeds |
| `before_write_vitest` | Before `/qakit.write.vitest` |
| `after_write_vitest` | After `/qakit.write.vitest` succeeds |
| `before_write_pom` | Before `/qakit.write.pom` |
| `after_write_pom` | After `/qakit.write.pom` succeeds |
| `before_ci_github_actions` | Before `/qakit.ci.github-actions` |
| `after_ci_github_actions` | After `/qakit.ci.github-actions` succeeds |
| `before_ci_jenkins` | Before `/qakit.ci.jenkins` |
| `after_ci_jenkins` | After `/qakit.ci.jenkins` succeeds |
| `before_maintain_flaky` | Before `/qakit.maintain.flaky` |
| `after_maintain_flaky` | After `/qakit.maintain.flaky` succeeds |
| `before_review_pr` | Before `/qakit.review.pr` |
| `after_review_pr` | After `/qakit.review.pr` succeeds |
| `before_review_bugreport` | Before `/qakit.review.bugreport` |
| `after_review_bugreport` | After `/qakit.review.bugreport` succeeds |

---

## Python API

### ExtensionManifest

```python
from qa_kit_cli.extensions import ExtensionManifest

manifest = ExtensionManifest.load_from_dir(Path("my-extension/"))
# manifest.id, manifest.name, manifest.version, manifest.description
# manifest.hooks: list[str]
# manifest.commands: dict[str, str]
```

### ExtensionManager

```python
from qa_kit_cli.extensions import ExtensionManager

manager = ExtensionManager(project_root=Path("."))

manager.add("git")                         # Install by ID (bundled) or path/URL
manager.add("./my-extension")             # Install from local path
manager.add("https://example.com/ext.zip")  # Install from remote archive

manager.list()                             # list[dict] with id, enabled
manager.set_enabled("git", False)          # Disable without removing
manager.set_enabled("git", True)           # Re-enable
manager.remove("git")                      # Uninstall
manager.active_manifests()                 # list[ExtensionManifest] — enabled only
```

### HookExecutor

```python
from qa_kit_cli.extensions import HookExecutor

executor = HookExecutor(project_root=Path("."))
results = executor.execute(manifests, "after_strategy")
# returns list[(extension_id, returncode)]
```

### HOOK_EVENTS

```python
from qa_kit_cli.extensions import HOOK_EVENTS
# tuple[str, ...] of all supported event names
```

---

## Extension State File

Extensions are persisted to `.qakit/extensions.json`:

```json
{
  "extensions": [
    { "id": "git", "enabled": true },
    { "id": "allure", "enabled": false }
  ]
}
```

Installed extension files are stored under `.qakit/extensions/<id>/`.

---

## Catalog Entry Format

To list an extension in the community catalog (`catalog.community.json`), add:

```json
{
  "id": "my-extension",
  "name": "My Extension",
  "version": "0.1.0",
  "description": "One-line description.",
  "bundled": false,
  "url": "https://github.com/org/my-extension/releases/download/v0.1.0/extension.zip",
  "author": "Your Name",
  "tags": ["reporting", "slack"]
}
```
