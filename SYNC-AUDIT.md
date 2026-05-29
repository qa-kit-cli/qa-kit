# Sync Audit — main branch vs PyPI v0.3.0

| Capability | In source? | Action needed |
|---|---|---|
| qakit self check (self group) | YES | No action |
| qakit self-check (root level, --json, exit codes) | NO | Add per Phase 1a |
| qakit integration install as primary | YES | No action |
| qakit integration uninstall as primary | YES | No action |
| qakit integration add/remove with deprecation notice | NO | Add notice per Phase 1b |
| qakit extension install as primary (split function) | NO | Split function per Phase 1b |
| qakit extension uninstall as primary (split function) | NO | Split function per Phase 1b |
| qakit preset install/uninstall aliases | NO | Add per Phase 1b |
| qakit extension resolve | YES | No action |
| qakit preset resolve | YES | No action |
| qakit workflow resume | YES | No action |
| qakit workflow status | YES | No action |
| qakit workflow add/remove/info/search | YES | No action |
| /qakit.tasks.issues template (110+ lines) | NO (has to-issues, 39 lines) | Create per Phase 1d |
| 37th COMMAND_MANIFEST entry (tasks.issues) | NO (has tasks.to-issues) | Rename per Phase 1d |
| Development Status :: 4 - Beta | YES | No action |
| version 0.3.0 in pyproject.toml | YES | No action |
