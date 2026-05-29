# /qakit.ci.report

Configure test result reporting in the CI pipeline.

## Description

Adds or updates the CI workflow to publish test results in multiple formats: JUnit XML (for CI dashboards and trend analysis), HTML report (for human review), and optionally Allure (rich multi-suite reporting). Also configures artefact upload with retention periods from `test-policy.md`.

## Usage

```
/qakit.ci.report [<format>]
```

## Arguments

Optional `<format>`:
- `"allure"` — configure Allure report generation and publish step
- `"junit"` (default) — JUnit XML + HTML report artefact upload
- `"all"` — JUnit + HTML + Allure

## Reads from memory

- `.qakit/memory/test-policy.md` — artefact retention periods, reporting requirements
- `.github/workflows/tests.yml` — the existing workflow to update

## Produces

Updates `.github/workflows/tests.yml` (or `Jenkinsfile`) to add:
- `--reporter=junit,html` flags to Playwright/Jest commands
- `actions/upload-artifact` steps for JUnit XML, HTML report, and Playwright traces on failure
- (Allure mode) Allure report generation and GitHub Pages or artefact publication

## Example

```
/qakit.ci.report allure
```

## Related commands

- `/qakit.ci.github-actions` — generates the base workflow that this command updates
- `/qakit.ci.jenkins` — configure reporting for Jenkins pipelines
