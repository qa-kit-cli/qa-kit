# QA Kit

This project uses [QA Kit](https://github.com/qa-kit-cli/qa-kit) — an AI-assisted QA automation toolkit.

## Active slash commands

All `/qakit.*` commands are installed in `.claude/commands/`. Use them to:
- `/qakit.strategy` — generate a QA strategy document
- `/qakit.testplan` — produce a structured test plan
- `/qakit.write.playwright` — write Playwright TypeScript tests
- `/qakit.write.jest` — write Jest unit/integration tests
- `/qakit.ci.github-actions` — generate CI/CD pipeline config
- `/qakit.review.pr` — QA-focused pull request review
- `/qakit.maintain.flaky` — diagnose and fix flaky tests

## Project memory

QA context files live in `.qakit/memory/`:
- `test-policy.md` — QA governance: coverage thresholds, approved frameworks, flakiness policy
- `qa-strategy.md` — risk areas and testing priorities for this project
- `test-plan.md` — live test plan with scope, environments, and exit criteria

Read these files before generating tests or CI config to ensure alignment with project standards.

## Test IDs

All test cases should be tagged with canonical IDs (`TC-001`, `TC-002`, …) as defined in `test-plan.md`.
