# /qakit.ci.github-actions

Generate a GitHub Actions workflow YAML for the project's test suite.

## Description

Produces `.github/workflows/tests.yml` — a complete, production-ready CI workflow with separate jobs for unit tests, integration tests, and E2E browser matrix. Includes concurrency cancellation, artefact upload (coverage, Playwright reports), and a coverage gate job.

Auto-detects the package manager (`npm`/`pnpm`/`yarn`), test framework scripts from `package.json`, and Playwright browser projects from `playwright.config.ts`.

## Usage

```
/qakit.ci.github-actions [<flags>]
```

## Arguments

Optional flags:
- `"add nightly E2E"` — adds a scheduled nightly full-matrix run
- `"use pnpm"` — forces pnpm instead of auto-detected package manager
- `"postgres service"` — adds a PostgreSQL service container for integration tests
- *(empty)* — auto-detects from project files

## Reads from memory

- `.qakit/memory/test-policy.md` — browser matrix, coverage threshold, CI gates
- `.qakit/memory/test-plan.md` — which test types exist and their trigger conditions

## Produces

`.github/workflows/tests.yml` with jobs: `unit`, `integration`, `e2e` (matrix), `coverage-gate`. Updated in place if it already exists.

## Example

```
/qakit.ci.github-actions
```

## Related commands

- `/qakit.ci.jenkins` — generates a Jenkinsfile instead
- `/qakit.ci.matrix` — design the browser/platform matrix first
- `/qakit.ci.report` — wire up JUnit XML / Allure reporting in the workflow
- `/qakit.ci.badges` — add status badges to README after generating the workflow
