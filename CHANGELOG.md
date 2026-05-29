# Changelog

All notable changes to QA Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.2.0] — 2026-05-29

### Added

#### Init parity
- `qakit init [project_name]` — create and initialize a new project directory
- `qakit init --here` — explicit alias for initializing the current directory
- `qakit init --force` — allow initialization in a non-empty directory
- `qakit init --integration-options="--skills"` — pass agent-specific options at init time
- `qakit init --preset <id>` — install one or more presets before registering commands
- `qakit init --ignore-agent-tools` — skip checking whether agent CLIs are on PATH
- `qakit init --script sh|ps` — select bash or PowerShell as the project script type
- `.qakit/config.json` — persists init options (`schema_version`, `script`, `branch_numbering`, `created_by`)
- New module `_integration_options.py` — parses shell-style `--integration-options` strings
- New module `project_config.py` — loads/saves `.qakit/config.json`

#### Skills mode (Phase 2)
- `IntegrationBase` gains `supports_skills`, `default_mode`, `get_skills_dir()`, `render_skill()`
- `SkillRegistrar` — installs per-command `SKILL.md` files into the agent's skills directory
- `ClaudeIntegration` supports skills mode: installs to `.claude/skills/qakit-*/SKILL.md` with YAML frontmatter
- `CodexIntegration` supports skills mode: installs to `.agents/skills/qakit-*/SKILL.md`
- `--integration-options="--skills"` on `init` / `integration install` enables skills mode

#### Safer integration lifecycle (Phase 3)
- `qakit integration install` — alias for `add`
- `qakit integration uninstall [--force]` — alias for `remove`; preserves locally-modified files by default
- `qakit integration use <key>` — switch active integration only if already installed
- `qakit integration switch` now accepts `--integration-options`
- `qakit integration upgrade [key] [--force]` — targets a single integration; blocks on modified files unless `--force`
- `manifest.get_modified_files()` — returns paths of installed files that have been locally modified
- `manifest.uninstall_files()` now returns `(removed, skipped)` tuple instead of a flat list

#### Runtime template override stack (Phase 4)
- New module `template_resolver.py` — `TemplateResolver` resolves templates through a 3-layer stack:
  1. Project-local overrides (`.qakit/templates/overrides/`)
  2. Installed presets by priority (`.qakit/presets/<id>/templates/commands/`)
  3. Core defaults (bundled `templates/commands/`)
- `CommandRegistrar` now uses `TemplateResolver`; missing templates are skipped gracefully
- `qakit preset resolve <file>` — shows the full resolution stack and winning layer

#### Preset system upgrade (Phase 5)
- `qakit preset search [query] [--tag] [--author]` — search bundled and catalog presets
- `qakit preset info <id>` — show preset metadata and compositions
- `qakit preset resolve <file>` — display template resolution stack
- `qakit preset set-priority <id> <n>` — alias for `priority`
- `qakit preset catalog list` — list active preset catalogs
- `qakit preset catalog add <url> [--name] [--priority] [--install-allowed]`
- `qakit preset catalog remove <name>`
- `preset add` accepts `--dev <path>` and `--from <url>` in addition to bundled IDs

#### Extension system upgrade (Phase 6)
- `qakit extension install` — alias for `add`
- `qakit extension uninstall` — alias for `remove`
- `qakit extension update [id]` — re-install to pick up the latest bundled version
- `qakit extension set-priority <id> <n>` — control hook execution order
- `qakit extension search [query] [--tag] [--author] [--verified]`
- `qakit extension info <id>` — show extension metadata and hooks
- `qakit extension catalog list/add/remove` — manage extension catalogs
- `ExtensionRegistry.list_bundled()` — enumerate bundled extensions
- `ExtensionManager.set_priority()` — persist priority in state file

#### Workflow engine upgrade (Phase 7)
- `engine.run()` now returns `(StepResult, RunState)` — persistent run state in `.qakit/workflows/runs/<run_id>/`
- New module `workflows/run_state.py` — `RunState` dataclass with `load`, `save`, `append_log`; `list_runs` helper
- `engine.resume(run_id)` — resume a paused or failed workflow from its saved step
- `engine.get_run(run_id)` / `engine.list_runs()` — inspect persisted runs
- New step type `IfStep` — conditional branch (`then`/`else`) based on an input value
- `qakit workflow run -i key=value` — pass inputs to a workflow at runtime (repeatable)
- `qakit workflow resume <run_id>` — resume a paused run
- `qakit workflow status [run_id]` — show run status or list all runs
- `qakit workflow add <source>` — copy a workflow into `.qakit/workflows/`
- `qakit workflow remove <workflow_id>` — remove a local workflow
- `qakit workflow info <workflow_id>` — show workflow metadata and steps
- `qakit workflow search [query]` — filter available workflows
- `qakit workflow catalog list/add/remove` — manage workflow catalogs
- 4 new bundled workflows: `full-qa-cycle`, `playwright-e2e`, `release-gate`, `regression-refresh`

#### New QA lifecycle commands — 36 total (was 29) (Phase 8)
- `/qakit.tasks` — generate a prioritized QA implementation task list from strategy and test plan
- `/qakit.checklist` — generate a QA readiness checklist for a feature or release
- `/qakit.traceability` — map requirements → test cases → test files → CI jobs
- `/qakit.regression` — build or update the regression suite with P0/P1/P2 tiers and quarantine tracking
- `/qakit.defects` — summarize defects, escaped bugs, root causes, and risk trends
- `/qakit.release-gate` — make a ship/no-ship decision from coverage, results, defects, and risk
- `/qakit.env` — define test environments, browser/device matrix, data rules, and service virtualization
- 14 new lifecycle hook events (`before_*/after_*`) for all new commands

#### QA differentiator artifacts (Phase 9)
- `.qakit/memory/test-tasks.md` — QA implementation task list with P0–P3 prioritization
- `.qakit/memory/qa-checklist.md` — release readiness checklist
- `.qakit/memory/traceability-matrix.md` — requirement → test case → CI job mapping
- `.qakit/memory/regression-suite.md` — tiered regression suite with quarantine tracking
- `.qakit/memory/defect-summary.md` — defect intelligence with escaped-defect analysis
- `.qakit/memory/release-gate.md` — ship/no-ship decision record
- `.qakit/memory/test-environments.md` — environment, browser matrix, and data governance spec
- All 7 memory files are created from templates on `qakit init`

### Changed

- `COMMAND_MANIFEST` extended from 29 to 36 entries
- `shared_infra.ensure_memory_files()` now creates all 10 memory files (was 3)
- `shared_infra.ensure_project_layout()` now creates `.qakit/templates/overrides/` and `.qakit/workflows/runs/`
- README command count updated from 26 to 36; new QA Lifecycle command table added
- `qakit init` quick-start examples in README updated to show new flags

### Fixed

- `uninstall_files()` — locally-modified command files are now preserved by default on `integration remove`; previously all managed files were deleted unconditionally

---

## [0.1.2] — 2026-05-29

### Fixed

- Command files installed by `qakit init` are now prefixed with `qakit.` for clear identification

## [0.1.1] — 2026-05-29

### Fixed

- Corrected GitHub org URLs to `qa-kit-cli`
- Simplified install commands to use PyPI

## [0.1.0] — 2026-05-29

### Added

- `qakit init` command — scaffolds `.qakit/` and installs slash commands into the active AI agent
- `qakit check` command — verifies prerequisites (Node.js, Playwright, Jest, etc.)
- `qakit integration` command group — add, remove, switch, list AI agent integrations
- `qakit preset` command group — add, remove, list, prioritize presets
- `qakit extension` command group — add, remove, list, enable, disable extensions
- `qakit workflow` command group — run named YAML-defined QA workflows
- **26 slash commands** across 5 categories (strategy, write, ci, maintain, review)
- **3 bundled presets**: `playwright`, `cypress`, `lean-qa`
- **3 bundled extensions**: `git`, `coverage-gate`, `test-numbering`
- **31 AI agent integrations**: Claude Code, GitHub Copilot, Gemini CLI, Cursor, Windsurf, and 26 more
- Extension system with 28 lifecycle hooks (`before_*/after_*`)
- Preset composition system (replace, prepend, append, wrap strategies)
- `.qakit/memory/` state directory with `test-policy.md`, `qa-strategy.md`, `test-plan.md`
- 6 core document templates: QA strategy, test plan, test tasks, bug report, test policy, coverage report
- Bash and PowerShell script pairs for cross-platform support
- `mypy --strict` type checking enforced in CI
