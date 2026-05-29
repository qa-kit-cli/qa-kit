# QA Kit

**AI-assisted QA automation toolkit for Playwright, Cypress, Jest, Vitest, Selenium, GitHub Actions, and Jenkins.**

QA Kit is a CLI toolkit purpose-built for QA automation engineers. It gives your AI coding assistant (Claude Code, GitHub Copilot, Gemini CLI, Cursor, Windsurf, and 25+ more) a complete set of slash commands for the full QA lifecycle — from strategy through release gate decisions.

Think of it as [Spec Kit](https://github.com/github/spec-kit) for QA: same architecture, same install method, but every command is tailored to testing workflows rather than feature specification.

Architecture details: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Install

```bash
uv tool install qa-kit-cli
```

Or with pipx:

```bash
pipx install qa-kit-cli
```

Or with pip:

```bash
pip install qa-kit-cli
```

---

## Quick Start

```bash
# Initialize QA Kit in your project (auto-detects your AI agent)
qakit init

# Or initialize with specific options
qakit init --integration codex --integration-options="--skills"
qakit init --preset playwright --integration claude
qakit init my-project --force --script ps

# In your AI agent, run the QA lifecycle commands
/qakit.policy
/qakit.strategy
/qakit.testplan
/qakit.traceability
/qakit.write.playwright
/qakit.ci.github-actions
/qakit.release-gate
```

---

## Slash Commands

QA Kit installs 37 slash commands into your AI agent's command directory.

### QA Strategy & Planning

| Command | Description |
|---|---|
| `/qakit.policy` | Create or update the project's test policy (governance, coverage thresholds, frameworks) |
| `/qakit.strategy` | Generate a QA strategy for a feature — risk areas, priorities, toolchain |
| `/qakit.testplan` | Produce a structured test plan: scope, entry/exit criteria, environments |
| `/qakit.coverage` | Analyze existing tests and report gaps against requirements |
| `/qakit.gaps` | Cross-reference requirements with the test plan and flag untested scenarios |
| `/qakit.clarify` | Resolve ambiguities in a QA strategy or test plan |
| `/qakit.pyramid` | Analyze test pyramid balance and recommend adjustments |

### QA Lifecycle

| Command | Description |
|---|---|
| `/qakit.tasks` | Generate a prioritized QA implementation task list from strategy and test plan |
| `/qakit.tasks.to-issues` | Convert QA implementation tasks into GitHub issue-ready drafts |
| `/qakit.checklist` | Generate a QA readiness checklist for a feature or release |
| `/qakit.traceability` | Map requirements → test cases → test files → CI jobs in a traceability matrix |
| `/qakit.regression` | Build or update the regression suite with P0/P1/P2 tiers and quarantine tracking |
| `/qakit.defects` | Summarize defects, escaped bugs, root causes, and risk trends |
| `/qakit.release-gate` | Make a ship/no-ship decision from coverage, test results, and defects |
| `/qakit.env` | Define test environments, browser/device matrix, data rules, and service virtualization |

### Test Writing

| Command | Description |
|---|---|
| `/qakit.write.playwright` | Write Playwright TypeScript tests with best-practice conventions |
| `/qakit.write.cypress` | Write Cypress TypeScript e2e/component tests |
| `/qakit.write.selenium` | Write Selenium WebDriver tests (Python or Java) |
| `/qakit.write.jest` | Write Jest unit/integration tests |
| `/qakit.write.vitest` | Write Vitest unit tests for Vite-based projects |
| `/qakit.write.pom` | Generate Page Object Model classes |
| `/qakit.write.fixtures` | Generate test fixtures, factories, and seed data |
| `/qakit.write.a11y` | Write automated accessibility tests (axe-core / Playwright) |
| `/qakit.write.visual` | Set up visual regression tests (Playwright screenshots / Percy) |
| `/qakit.write.api` | Write API contract tests (REST/GraphQL) |

### CI/CD Pipeline

| Command | Description |
|---|---|
| `/qakit.ci.github-actions` | Generate GitHub Actions workflow with matrix strategy |
| `/qakit.ci.jenkins` | Generate a declarative Jenkinsfile for test execution |
| `/qakit.ci.matrix` | Design cross-browser/platform test matrix |
| `/qakit.ci.badges` | Add test coverage and quality badges to README |
| `/qakit.ci.report` | Configure Allure / JUnit XML / HTML reporting in CI |

### Test Maintenance

| Command | Description |
|---|---|
| `/qakit.maintain.flaky` | Diagnose and fix flaky tests |
| `/qakit.maintain.refactor` | Refactor tests to current framework conventions |
| `/qakit.maintain.data` | Audit and clean up test data and fixtures |
| `/qakit.maintain.upgrade` | Upgrade tests to a new framework version |

### QA Review

| Command | Description |
|---|---|
| `/qakit.review.pr` | Review a PR from a QA perspective |
| `/qakit.review.bugreport` | Generate a structured, Jira-ready bug report |
| `/qakit.review.accessibility` | Audit a page/component for WCAG 2.1 AA compliance |

---

## Presets

Presets tailor commands to your framework stack. Three are bundled:

```bash
qakit preset add playwright   # TypeScript + Playwright conventions
qakit preset add cypress      # Cypress Component Testing + E2E
qakit preset add lean-qa      # Minimal workflow for small teams
```

---

## Extensions

Extensions add integrations with external tools:

```bash
qakit extension add allure        # Allure report generation
qakit extension add testrail      # TestRail sync
qakit extension add jira          # Jira defect tracking
qakit extension add browserstack  # Cross-browser cloud testing
```

---

## Supported AI Agents

QA Kit works with 32 AI coding agents including:

Claude Code · GitHub Copilot · Gemini CLI · Cursor · Windsurf · Amp · OpenCode · Forge · Roo · Kiro CLI · Junie · Devin · Tabnine · and more.

---

## Bundled Workflows

| Workflow ID | Steps |
|---|---|
| `full-qa-cycle` | `policy` → `strategy` → `testplan` → `tasks` → `write.playwright` → `ci.github-actions` |
| `playwright-e2e` | `strategy` → `write.playwright` → `write.pom` → `ci.github-actions` |
| `release-gate` | `coverage` → `traceability` → `regression` → `defects` → `release-gate` |
| `regression-refresh` | `regression` → `maintain.flaky` → `maintain.data` → `ci.github-actions` |

---

## CLI Reference

```
qakit init [PROJECT_NAME]
  --here                              Initialize in current directory
  --force                             Skip confirmation in non-empty directories
  --integration, -i TEXT              AI agent to configure
  --integration-options TEXT          Pass-through options (e.g. "--skills")
  --ignore-agent-tools                Skip CLI tool version checks
  --script [sh|ps]                    Script type (default: platform-aware)
  --no-git                            Skip git initialization
  --branch-numbering [sequential|timestamp]
  --preset TEXT                       Install preset at init (repeatable)

qakit integration install|add <key>       Install an AI agent integration
qakit integration uninstall|remove <key>  Uninstall an AI agent integration
qakit integration switch <key>            Switch to a different integration
qakit integration use <key>               Set active integration without reinstalling
qakit integration upgrade [key]           Reinstall with updated templates
qakit integration list [--catalog]        List integrations

qakit extension install|add <id>          Install an extension
  --priority N                            Set priority (default: 10)
  --dev <path>                            Install from local path
  --from <url>                            Install from URL
qakit extension uninstall|remove <id>
  --keep-config                           Back up config files instead of deleting
  --force                                 Remove immediately
qakit extension update <id>               Update to latest version
qakit extension list [--available] [--all]
qakit extension search [query]            Search catalog
qakit extension info <id>                 Show extension details
qakit extension enable/disable <id>
qakit extension resolve <template>        Show 4-layer resolution stack

qakit preset add <id> [--priority N]
qakit preset remove <id>
qakit preset list
qakit preset search [query]
qakit preset info <id>
qakit preset priority <id> <n>
qakit preset enable/disable <id>
qakit preset resolve <template>

qakit workflow run <id> [-i key=value]
qakit workflow list
qakit workflow resume
qakit workflow status

qakit version [--features] [--json]
qakit check
qakit self update
qakit self check
```

---

## License

MIT — see [LICENSE](LICENSE).
