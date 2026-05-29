# /qakit.ci.jenkins

Generate a declarative Jenkinsfile for test execution with parallel stages.

## Description

Produces a `Jenkinsfile` (declarative pipeline) that runs unit, integration, and E2E tests in parallel stages. Includes test result publication (`junit`), HTML report archiving, and a coverage gate check.

## Usage

```
/qakit.ci.jenkins [<flags>]
```

## Arguments

Optional flags:
- `"use docker"` — wraps stages in `agent { docker { … } }` blocks
- `"add Allure"` — adds Allure report generation and publishing steps
- *(empty)* — infers from project files and `test-policy.md`

## Reads from memory

- `.qakit/memory/test-policy.md` — browser matrix, coverage threshold, CI gates
- `.qakit/memory/test-plan.md` — test types, trigger conditions

## Produces

`Jenkinsfile` in the project root. Sections: `environment`, `stages` (Install → Unit → Integration → E2E → Coverage Gate), `post` (always: publish results, on failure: archive artefacts).

## Example

```
/qakit.ci.jenkins
```

## Related commands

- `/qakit.ci.github-actions` — generate a GitHub Actions workflow instead
- `/qakit.ci.report` — configure Allure or JUnit reporting within the pipeline
