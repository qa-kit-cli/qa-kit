# QA Kit — Pre-Implementation Plan

## Context

Spec Kit (github/spec-kit) is GitHub's AI-assisted, specification-driven development toolkit. It ships a Python CLI (`specify`), slash commands as Markdown templates, an extension/preset/integration system, and supports 30+ AI coding agents. The core workflow: write specs → plan → generate tasks → implement.

QA Kit mirrors that architecture exactly — same CLI patterns, same extension/preset/integration system, same install method (`uv tool install`) — but is purpose-built for QA automation engineers. Where Spec Kit is spec→code, QA Kit is risk→tests. QA Kit must be installable, extensible, and immediately useful out of the box.

---

## 1. Complete Folder & File Structure

```
qa-kit/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                        # pytest on every push/PR
│   │   ├── release.yml                   # Publish to PyPI on version tag
│   │   └── lint.yml                      # ruff + mypy checks
│   ├── CODEOWNERS
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── docs/                                 # DocFX-based documentation site
│   ├── index.md
│   ├── getting-started.md
│   ├── commands/                         # One page per slash command
│   ├── presets/
│   ├── extensions/
│   └── docfx.json
│
├── src/qa_kit_cli/
│   ├── __init__.py                       # Typer app + main() entry point
│   ├── _agent_config.py                  # Derives AGENT_CONFIGS from integration registry
│   ├── _assets.py                        # Locates bundled core_pack assets (wheel vs dev)
│   ├── _console.py                       # Rich-based StepTracker, banners, arrow-key select
│   ├── _github_http.py                   # HTTPS helper for catalog/extension fetches
│   ├── _utils.py                         # run_command, is_git_repo, merge_json, atomic writes
│   ├── _version.py                       # __version__ via importlib.metadata
│   ├── agents.py                         # CommandRegistrar — writes commands to all agent dirs
│   ├── authentication/
│   │   ├── __init__.py
│   │   └── token_store.py                # Secure storage for Jira/TestRail/Allure tokens
│   ├── catalogs.py                       # CatalogStackBase + integration/extension catalogs
│   ├── extensions.py                     # ExtensionManifest, Registry, Manager, HookExecutor
│   ├── presets.py                        # PresetManifest, Registry, Manager, PresetResolver
│   ├── shared_infra.py                   # Install/refresh .qakit/scripts and .qakit/templates
│   ├── integration_runtime.py            # Resolve integration options, invoke separator logic
│   ├── integration_state.py              # Read/write .qakit/integration.json
│   ├── commands/
│   │   ├── __init__.py                   # Registers all command groups into Typer app
│   │   ├── init.py                       # `qakit init` — scaffold a project
│   │   ├── integration.py                # `qakit integration *`
│   │   ├── extension.py                  # `qakit extension *`
│   │   ├── preset.py                     # `qakit preset *`
│   │   └── workflow.py                   # `qakit workflow *`
│   ├── integrations/
│   │   ├── __init__.py                   # _register_builtins() call
│   │   ├── base.py                       # IntegrationBase, MarkdownIntegration, TomlIntegration
│   │   ├── manifest.py                   # SHA-256 hash manifest for safe uninstall
│   │   ├── catalog.py                    # IntegrationCatalog (fetches integrations/catalog.json)
│   │   ├── claude/       __init__.py     # .claude/commands/, format=markdown
│   │   ├── copilot/      __init__.py     # .copilot/commands/
│   │   ├── gemini/       __init__.py     # .gemini/commands/, format=toml
│   │   ├── cursor_agent/ __init__.py
│   │   ├── windsurf/     __init__.py
│   │   ├── amp/          __init__.py
│   │   ├── codex/        __init__.py
│   │   ├── devin/        __init__.py
│   │   ├── forge/        __init__.py
│   │   ├── kiro_cli/     __init__.py
│   │   ├── junie/        __init__.py
│   │   ├── auggie/       __init__.py
│   │   ├── shai/         __init__.py
│   │   ├── tabnine/      __init__.py
│   │   ├── roo/          __init__.py
│   │   ├── kilocode/     __init__.py
│   │   ├── qwen/         __init__.py
│   │   ├── opencode/     __init__.py
│   │   ├── goose/        __init__.py
│   │   ├── trae/         __init__.py
│   │   ├── codebuddy/    __init__.py
│   │   ├── bob/          __init__.py
│   │   ├── kimi/         __init__.py
│   │   ├── lingma/       __init__.py
│   │   ├── qodercli/     __init__.py
│   │   ├── pi/           __init__.py
│   │   ├── iflow/        __init__.py
│   │   ├── vibe/         __init__.py
│   │   ├── hermes/       __init__.py
│   │   └── generic/      __init__.py    # Bring-your-own-agent fallback
│   └── workflows/
│       ├── base.py                       # StepBase, StepContext, StepResult ABCs
│       ├── catalog.py                    # WorkflowCatalog (remote + bundled)
│       ├── engine.py                     # WorkflowEngine — resolves and executes YAML workflows
│       ├── expressions.py                # Jinja2-lite {{ inputs.x }} expression evaluator
│       └── steps/
│           ├── __init__.py
│           ├── command_step.py           # Dispatches a slash command to an agent
│           ├── gate_step.py              # Interactive approve/reject gate
│           ├── shell_step.py             # Runs a shell command
│           └── parallel_step.py         # Fan-out parallel execution
│
├── templates/
│   ├── qa-strategy-template.md           # QA equivalent of spec-template.md
│   ├── test-plan-template.md             # QA equivalent of plan-template.md
│   ├── test-tasks-template.md            # QA equivalent of tasks-template.md
│   ├── bug-report-template.md            # Structured bug report with repro steps
│   ├── test-policy-template.md           # QA equivalent of constitution-template.md
│   ├── coverage-report-template.md       # Gap analysis output template
│   └── commands/                         # All 26 slash command .md files
│       ├── strategy.md
│       ├── testplan.md
│       ├── coverage.md
│       ├── gaps.md
│       ├── policy.md
│       ├── clarify.md
│       ├── pyramid.md
│       ├── write.playwright.md
│       ├── write.cypress.md
│       ├── write.selenium.md
│       ├── write.jest.md
│       ├── write.vitest.md
│       ├── write.pom.md
│       ├── write.fixtures.md
│       ├── write.a11y.md
│       ├── write.visual.md
│       ├── write.api.md
│       ├── ci.github-actions.md
│       ├── ci.jenkins.md
│       ├── ci.matrix.md
│       ├── ci.badges.md
│       ├── ci.report.md
│       ├── maintain.flaky.md
│       ├── maintain.refactor.md
│       ├── maintain.data.md
│       ├── maintain.upgrade.md
│       ├── review.pr.md
│       ├── review.bugreport.md
│       └── review.accessibility.md
│
├── presets/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── PUBLISHING.md
│   ├── catalog.json                      # Bundled preset catalog
│   ├── catalog.community.json
│   ├── playwright/                       # Bundled: Playwright + TypeScript conventions
│   │   ├── preset.yml
│   │   └── templates/commands/
│   ├── cypress/                          # Bundled: Cypress + component testing
│   │   ├── preset.yml
│   │   └── templates/commands/
│   └── lean-qa/                          # Bundled: minimal strategy→plan→write→ci
│       ├── preset.yml
│       └── templates/commands/
│
├── extensions/
│   ├── EXTENSION-API-REFERENCE.md
│   ├── EXTENSION-DEVELOPMENT-GUIDE.md
│   ├── EXTENSION-PUBLISHING-GUIDE.md
│   ├── EXTENSION-USER-GUIDE.md
│   ├── RFC-EXTENSION-SYSTEM.md
│   ├── catalog.json
│   └── catalog.community.json
│
├── integrations/
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── catalog.json                      # 31+ agent integration entries
│   └── catalog.community.json
│
├── workflows/
│   └── qakit/
│       └── workflow.yml                  # Full QA cycle: strategy→plan→write→ci
│
├── scripts/
│   ├── bash/
│   │   ├── common.sh
│   │   ├── check-prerequisites.sh
│   │   ├── setup-strategy.sh
│   │   ├── setup-testplan.sh
│   │   └── setup-tests.sh
│   └── powershell/
│       ├── common.ps1
│       ├── check-prerequisites.ps1
│       ├── setup-strategy.ps1
│       ├── setup-testplan.ps1
│       └── setup-tests.ps1
│
├── tests/
│   ├── conftest.py                       # Shared fixtures: tmp project dirs, mock catalogs
│   ├── test_init.py
│   ├── test_extensions.py
│   ├── test_presets.py
│   ├── test_integration_state.py
│   ├── test_agents.py
│   ├── test_shared_infra.py
│   └── test_workflows.py
│
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── DEVELOPMENT.md
├── SECURITY.md
└── LICENSE                               # MIT
```

---

## 2. CLI Commands

```
qakit init                          Scaffold a project with QA Kit
qakit check                         Verify prerequisites (node, playwright, jest, etc.)
qakit version                       Show CLI version and system info
qakit integration add <key>
qakit integration remove <key>
qakit integration switch <key>
qakit integration list
qakit integration upgrade
qakit extension add <id|url|path>
qakit extension remove <id>
qakit extension list
qakit extension enable <id>
qakit extension disable <id>
qakit preset add <id|url|path>
qakit preset remove <id>
qakit preset list
qakit preset priority <id> <n>
qakit preset enable/disable <id>
qakit workflow run <id>
qakit workflow list
qakit self update
```

Entry point: `qakit = "qa_kit_cli:main"` in pyproject.toml.

---

## 3. All Slash Commands (26 total)

### Category A — QA Strategy & Planning (7 commands)

| Command | Description |
|---|---|
| `qakit.strategy` | Generate a full QA strategy doc for a feature/project — risk areas, testing priorities, toolchain |
| `qakit.testplan` | Produce a structured test plan from a QA strategy: scope, entry/exit criteria, environments, schedule |
| `qakit.coverage` | Analyze existing test files and report coverage gaps against requirements or the active test plan |
| `qakit.gaps` | Cross-reference feature requirements with the test plan and flag untested scenarios |
| `qakit.policy` | Create or update `test-policy.md` — the project's QA governance doc (QA equivalent of `constitution`) |
| `qakit.clarify` | Identify and resolve ambiguities in a QA strategy or test plan via targeted questions |
| `qakit.pyramid` | Analyze the project's test pyramid (unit/integration/e2e ratio) and recommend adjustments |

### Category B — Test Writing (10 commands)

| Command | Description |
|---|---|
| `qakit.write.playwright` | Write Playwright TypeScript tests — `page.getByRole`, `expect`, `test.describe/step` conventions |
| `qakit.write.cypress` | Write Cypress TypeScript e2e/component tests with `cy.intercept`, `cy.fixture` conventions |
| `qakit.write.selenium` | Write Selenium WebDriver tests (Python or Java) for a given user flow |
| `qakit.write.jest` | Write Jest unit/integration tests with mocks, spies, and coverage annotations |
| `qakit.write.vitest` | Write Vitest unit tests for Vite-based projects with `vi.mock` and inline snapshots |
| `qakit.write.pom` | Generate Page Object Model classes for a given set of pages or UI components |
| `qakit.write.fixtures` | Generate test fixtures, factory functions, and seed data for a test suite |
| `qakit.write.a11y` | Write automated accessibility tests using axe-core via Playwright accessibility APIs |
| `qakit.write.visual` | Set up and write visual regression tests using Playwright screenshots or Percy |
| `qakit.write.api` | Write API contract tests (REST/GraphQL) using Supertest or Playwright APIRequestContext |

### Category C — CI/CD Pipeline (5 commands)

| Command | Description |
|---|---|
| `qakit.ci.github-actions` | Generate a GitHub Actions workflow YAML for the project's test suite with matrix strategy |
| `qakit.ci.jenkins` | Generate a declarative Jenkinsfile for test execution with parallel stages |
| `qakit.ci.matrix` | Design a cross-browser/platform test matrix and emit the CI config for it |
| `qakit.ci.badges` | Add test coverage, pipeline status, and quality badges to the project README |
| `qakit.ci.report` | Configure test result reporting (JUnit XML, HTML, Allure) in the CI pipeline |

### Category D — Test Maintenance (4 commands)

| Command | Description |
|---|---|
| `qakit.maintain.flaky` | Diagnose a flaky test: identify root cause, suggest retry strategy or deterministic fix |
| `qakit.maintain.refactor` | Refactor an existing test file to follow current framework conventions and reduce duplication |
| `qakit.maintain.data` | Audit and clean up test data: orphaned fixtures, hardcoded values, environment coupling |
| `qakit.maintain.upgrade` | Upgrade a test suite from one framework version to another (e.g., Playwright v1.40 → v1.50) |

### Category E — QA Review (3 commands)

| Command | Description |
|---|---|
| `qakit.review.pr` | Review a pull request from a QA perspective: coverage delta, missing edge cases, risk areas |
| `qakit.review.bugreport` | Generate a structured bug report with repro steps, severity, expected/actual, and Jira formatting |
| `qakit.review.accessibility` | Audit a component or page for WCAG 2.1 AA compliance criteria |

---

## 4. Presets — Prioritized Build Order

### P1 — `playwright` (bundled at v0.1.0)
Tailors `write.playwright`, `ci.github-actions`, `write.pom`, `write.visual` to Playwright idioms:
TypeScript, `test.describe/step`, `expect` from `@playwright/test`, `page.getByRole` locators,
`playwright.config.ts` conventions. Composition: `write.playwright` = replace, `write.a11y` = append,
`ci.github-actions` = replace, `write.visual` = replace.

### P2 — `cypress` (bundled at v0.1.0)
Tailors commands for Cypress Component Testing + E2E: `cy.intercept`, `cy.fixture`, Cypress Cloud.

### P3 — `lean-qa` (bundled at v0.1.0)
Minimal workflow preset: strategy → testplan → write → ci, no ceremony. For solo QA engineers and
small teams. Mirrors Spec Kit's `lean` preset.

### P4 — `full-stack` (v0.2)
Multi-framework: Jest (unit) + Playwright (e2e) + pyramid ratio tracking via `qakit.pyramid`.

### P5 — `enterprise-qa` (v0.3)
TestRail sync hooks, Jira defect tracking hooks, mandatory coverage gates in CI, `test-policy.md`
governance enforcement. For regulated/enterprise environments.

### P6 — `selenium-java` (community)
JUnit 5 + TestNG + Selenium WebDriver, Maven/Gradle CI config.

### P7 — `mobile-qa` (community)
Appium + Detox patterns for React Native and native iOS/Android.

---

## 5. Extensions

### Built-In (bundled in `core_pack`)

**`git`** — Feature branch creation and validation. Hooks: `after_strategy`, `after_testplan`.

**`coverage-gate`** — Enforces minimum coverage thresholds in CI.
Provides `qakit.ext.coverage-gate.enforce`. Hooks: `before_ci_github-actions`, `after_write_playwright`.

**`test-numbering`** — Assigns canonical IDs (TC-001, TC-002) to test cases.
Hooks: `after_write_playwright`, `after_write_jest`. Makes coverage reporting deterministic.

### Built-In (v0.2)

**`allure`** — Allure report generation and upload. Hooks: `after_ci_github-actions`, `after_ci_jenkins`.

**`testrail`** — Sync test plans to TestRail, post results from CI. Requires `TESTRAIL_URL` + `TESTRAIL_API_KEY`.

**`jira`** — Create Jira tickets from `qakit.review.bugreport` output. Hooks: `after_review_bugreport`.

### Recommended Community Extensions

`percy`, `browserstack`, `lighthouse`, `axe-reporter`, `k6-load`, `cypress-cloud`

### Lifecycle Hook Events (28 total)

```
before/after_strategy, before/after_testplan, before/after_coverage, before/after_gaps
before/after_policy, before/after_write_playwright, before/after_write_cypress
before/after_write_jest, before/after_write_vitest, before/after_write_pom
before/after_ci_github_actions, before/after_ci_jenkins
before/after_maintain_flaky, before/after_review_pr, before/after_review_bugreport
```

---

## 6. Integrations (31 total)

**Tier 1 (launch, fully tested):** claude, copilot, gemini, cursor-agent, windsurf

**Tier 2 (launch, verified):** amp, codex, opencode, forge, roo

**Tier 3 (launch, community-verified):** kiro-cli, junie, devin, auggie, tabnine, shai, kilocode

**Tier 4 (launch, basic support):** qwen, goose, trae, codebuddy, bob, kimi, lingma, qodercli,
pi, iflow, vibe, hermes, generic (bring-your-own-agent fallback)

All integrations use the same Python class pattern as Spec Kit:
```python
class ClaudeIntegration(MarkdownIntegration):
    key = "claude"
    config = {"name": "Claude Code", "folder": ".claude/commands/", ...}
    registrar_config = {"dir": ".claude/commands/", "format": "markdown", ...}
```

---

## 7. Tech Stack

```toml
[project]
name = "qa-kit-cli"
version = "0.1.0.dev0"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.14.0",
    "click>=8.2.1",
    "rich>=14.0",
    "platformdirs>=4.0",
    "readchar>=4.0",
    "pyyaml>=6.0",
    "packaging>=23.0",
    "pathspec>=0.12.0",
    "json5>=0.13.0",
]

[project.scripts]
qakit = "qa_kit_cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.optional-dependencies]
test = ["pytest>=8.0", "pytest-cov>=5.0", "pytest-mock>=3.0"]
dev  = ["ruff>=0.8.0", "mypy>=1.11", "types-PyYAML"]
```

Asset bundling (same pattern as Spec Kit's `force-include`): templates, commands, scripts,
bundled extensions, presets, and workflows are all included in `core_pack/` in the wheel.

---

## 8. Key Improvements Over Spec Kit

| Area | Spec Kit | QA Kit |
|---|---|---|
| Framework awareness | Framework-agnostic (intentional) | Framework-specific commands with deep Playwright/Cypress/Jest idioms |
| Test traceability | None | `test-numbering` extension: TC-001 → test plan requirement mapping |
| Memory model | `constitution.md` (5 generic principles) | `test-policy.md` with coverage thresholds, flakiness policy, defect taxonomy |
| Bundled presets | 1 (`lean`) | 3 (`playwright`, `cypress`, `lean-qa`) |
| Bundled extensions | 1 (`git`) | 3 (`git`, `coverage-gate`, `test-numbering`) |
| CI commands | None | 5 CI commands (GitHub Actions, Jenkins, matrix, badges, reporting) |
| Maintenance commands | None | 4 dedicated maintenance commands |
| Bug reporting | None | `qakit.review.bugreport` generates structured, Jira-ready reports |
| Type safety | No mypy | `mypy --strict` in CI from day one |

---

## 9. State Directory Structure (`.qakit/memory/`)

### `test-policy.md` — The QA Constitution

Sections:
- **Coverage Thresholds** — unit ≥ X%, integration ≥ Y%, critical E2E paths list
- **Approved Frameworks** — E2E (Playwright/Cypress/Selenium), Unit (Jest/Vitest), API, Visual, A11y
- **Environment Matrix** — browser/OS/version combinations
- **Test Organization** — file naming, directory layout, POM requirement
- **Flakiness Policy** — max flakiness rate, retry strategy, quarantine process
- **Defect Severity Taxonomy** — P0/P1/P2/P3 definitions
- **CI/CD Gates** — PR gate, main branch gate, release gate

### `qa-strategy.md`
Output of `qakit.strategy`. Risk areas, testing priorities, toolchain decisions, team responsibilities.

### `test-plan.md`
Output of `qakit.testplan`. Live test plan: scope, in-scope/out-of-scope, test types, environments,
schedule, exit criteria.

---

## 10. Core Templates

### `qa-strategy-template.md` (equivalent of `spec-template.md`)
- Feature Overview and Risk Classification
- User Journeys to Test (P1/P2/P3, each independently testable)
- Test Types Required (unit/integration/e2e/visual/a11y/performance)
- Acceptance Criteria (Given-When-Then, measurable)
- Data Requirements (test data, PII concerns)
- Environment Requirements
- Edge Cases and Negative Scenarios
- Out of Scope (explicit exclusions)
- `[NEEDS CLARIFICATION]` markers (max 3)

### `test-plan-template.md` (equivalent of `plan-template.md`)
- Summary (scope, objectives, success metrics)
- Technical Context (framework versions, CI environment)
- Policy Check (verifies alignment with `test-policy.md` before proceeding)
- Test Architecture (pyramid breakdown: % unit / % integration / % e2e)
- Test Suite Layout (directory structure, naming conventions)
- Environment Matrix
- Data Model (fixtures, factories, seed scripts)
- CI/CD Integration (which pipeline stages run which test types)

### `test-tasks-template.md` (equivalent of `tasks-template.md`)
- Phase 1: Setup (framework config, directory structure, CI skeleton)
- Phase 2: Foundation (shared fixtures, POM base classes, auth helpers)
- Phase 3+: Test Suites per User Journey (one phase per P1/P2/P3 journey)
- Phase N: Polish (coverage report, badge wiring, flakiness baseline)

Task format: `[TC-NNN] [P?] [Journey-N] Description — path/to/test.spec.ts`

### `bug-report-template.md` (QA-specific)
- ID, Severity (P0-P3), Priority, Status, Reporter, Date
- Environment (version, browser/OS, test env)
- Summary, Steps to Reproduce, Expected vs Actual
- Evidence (screenshots, logs, HAR files, linked TC IDs)
- Root Cause Hypothesis, Suggested Fix

### `coverage-report-template.md` (QA-specific)
Output of `qakit.coverage`. Maps each requirement → test IDs, flags gaps, reports pyramid ratio.

---

## Verification Plan

1. `qakit init` scaffolds `.qakit/` and installs commands to the active agent's directory
2. Run `qakit.strategy` in Claude Code → produces `.qakit/memory/qa-strategy.md`
3. Run `qakit.testplan` → produces `.qakit/memory/test-plan.md`
4. Run `qakit.write.playwright` → produces a `*.spec.ts` file following Playwright conventions
5. Run `qakit.ci.github-actions` → produces `.github/workflows/tests.yml` with matrix config
6. Run `pytest tests/` — all unit tests pass
7. `uv tool install qa-kit-cli --from git+https://github.com/...` installs cleanly and `qakit --help` works
