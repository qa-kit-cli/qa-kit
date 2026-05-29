# /qakit.ci.badges

Add test coverage, pipeline status, and quality badges to the project README.

## Description

Reads the project's CI configuration and generates Markdown badge lines for `README.md`: pipeline status (GitHub Actions), coverage percentage (Codecov or `jest --coverage`), and optionally Playwright test status. Inserts them at the top of the README, after the title.

## Usage

```
/qakit.ci.badges [<options>]
```

## Arguments

Optional `<options>`:
- `"codecov"` — generates a Codecov badge (requires Codecov integration)
- `"no coverage"` — pipeline status badge only
- *(empty)* — generates status + coverage badges, infers coverage provider from project

## Reads from memory

- `.qakit/memory/test-plan.md` — identifies CI events and job names for badge URLs

## Produces

Badge Markdown inserted at the top of `README.md`:
```markdown
[![Tests](https://github.com/org/repo/actions/workflows/tests.yml/badge.svg)](https://github.com/org/repo/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/org/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/org/repo)
```

## Example

```
/qakit.ci.badges
```

## Related commands

- `/qakit.ci.github-actions` — generate the workflow that powers these badges
- `/qakit.ci.report` — wire up coverage reporting that feeds the badge
