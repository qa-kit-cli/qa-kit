# QA Kit

**AI-assisted QA automation toolkit for Playwright, Cypress, Jest, Vitest, Selenium, GitHub Actions, and Jenkins.**

QA Kit is a CLI toolkit purpose-built for QA automation engineers. It gives your AI coding assistant (Claude Code, GitHub Copilot, Gemini CLI, Cursor, Windsurf, and 25+ more) a complete set of slash commands for the full QA lifecycle — from strategy through CI/CD.

Think of it as [Spec Kit](https://github.com/github/spec-kit) for QA: same architecture, same install method, but every command is tailored to testing workflows rather than feature specification.

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
# Initialize QA Kit in your project (picks up your AI agent automatically)
qakit init

# In your AI agent, run the first command
/qakit.policy
/qakit.strategy
/qakit.testplan
/qakit.write.playwright
/qakit.ci.github-actions
```

---

## Slash Commands

QA Kit installs 26 slash commands into your AI agent's command directory.

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

QA Kit works with 31 AI coding agents including:

Claude Code · GitHub Copilot · Gemini CLI · Cursor · Windsurf · Amp · OpenCode · Forge · Roo · Kiro CLI · Junie · Devin · Tabnine · and more.

---

## CLI Reference

```
qakit init                          Scaffold .qakit/ and install commands
qakit check                         Verify prerequisites (node, playwright, jest)
qakit version                       Show version info

qakit integration add <agent>       Install an AI agent integration
qakit integration switch <agent>    Change the active agent
qakit integration list              List installed integrations

qakit preset add <id>               Install a preset
qakit preset list                   List installed presets
qakit preset priority <id> <n>      Set preset priority

qakit extension add <id>            Install an extension
qakit extension list                List installed extensions

qakit workflow run <id>             Run a named QA workflow
```

---

## License

MIT — see [LICENSE](LICENSE).
