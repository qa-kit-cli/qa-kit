---
command: qakit.ci.badges
description: Add test coverage, pipeline status, and quality badges to the project README.
---

# /qakit.ci.badges

Add test quality badges to the project README.

## Context

**Input:** $ARGUMENTS
*(Optional: badge provider preferences, e.g. "use shields.io for all" or "add Codecov badge".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — coverage thresholds (to set the badge colour thresholds)

Inspect:
- `README.md` — insert badges below the project title, above the description
- `.github/workflows/` — get the workflow names for GitHub Actions status badges
- `package.json` — detect test frameworks for appropriate badges
- Whether Codecov, Coveralls, or a custom coverage reporter is configured

## Badge types to add

### 1. Pipeline status (GitHub Actions)

```markdown
[![Tests](https://github.com/<owner>/<repo>/actions/workflows/tests.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/tests.yml)
[![Lint](https://github.com/<owner>/<repo>/actions/workflows/lint.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/lint.yml)
```

Replace `<owner>/<repo>` with the actual repository path from `git remote get-url origin`.

### 2. Coverage badge

If Codecov is configured:
```markdown
[![codecov](https://codecov.io/gh/<owner>/<repo>/branch/main/graph/badge.svg)](https://codecov.io/gh/<owner>/<repo>)
```

If using a custom coverage reporter, use shields.io with an endpoint:
```markdown
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)](./coverage/lcov-report/index.html)
```

Set colour thresholds based on `test-policy.md` unit coverage threshold:
- < threshold − 20%: red
- < threshold: yellow
- ≥ threshold: brightgreen

### 3. Test count / last run

```markdown
[![Playwright Tests](https://img.shields.io/badge/playwright-E2E-45ba4b?logo=playwright)](https://github.com/<owner>/<repo>/actions/workflows/tests.yml)
```

### 4. Quality / framework badges

```markdown
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178C6?logo=typescript)](tsconfig.json)
[![Playwright](https://img.shields.io/badge/Playwright-tested-45ba4b?logo=playwright)](playwright.config.ts)
[![License](https://img.shields.io/github/license/<owner>/<repo>)](LICENSE)
```

## README placement

Insert the badge block immediately after the `# Project Title` line, before the first paragraph:

```markdown
# Project Name

[![Tests](…)](…) [![Coverage](…)](…) [![License](…)](…)

> One-line description of the project.
```

## Codecov setup (if not already configured)

If Codecov is not yet wired, add this step to the unit test job in `.github/workflows/tests.yml`:

```yaml
- uses: codecov/codecov-action@v4
  with:
    files: ./coverage/lcov.info
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```

## Output

1. Updated `README.md` with the badge block
2. (If needed) updated `.github/workflows/tests.yml` to upload coverage to Codecov

After writing, print the rendered badge Markdown for review and list which placeholders (`<owner>`, `<repo>`) must still be replaced.
