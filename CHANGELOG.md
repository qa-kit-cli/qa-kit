# Changelog

All notable changes to QA Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
