---
command: qakit.ci.report
description: Configure test result reporting (JUnit XML, HTML, Allure) in the CI pipeline.
---

# /qakit.ci.report

Configure test result reporting for the CI pipeline.

## Context

**Input:** $ARGUMENTS
*(Optional: reporting tool preference, e.g. "add Allure", "configure JUnit XML for Jenkins", or "HTML report only".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — CI/CD gates and any reporting requirements
- `.github/workflows/tests.yml` (or `Jenkinsfile`) — to add reporter steps without breaking existing config

Detect installed reporters: check `package.json` for `allure-playwright`, `allure-jest`, `jest-junit`, etc.

## Reporter configurations

### Playwright — multiple reporters

Update `playwright.config.ts`:
```typescript
reporter: [
  ['list'],                            // terminal output during run
  ['junit', { outputFile: 'playwright-results/results.xml' }],
  ['html', { outputFolder: 'playwright-report', open: 'never' }],
  // Add if allure-playwright is installed:
  ['allure-playwright', { outputFolder: 'allure-results' }],
],
```

### Jest — JUnit + coverage

`jest.config.ts` or `package.json`:
```json
{
  "jest": {
    "reporters": [
      "default",
      ["jest-junit", {
        "outputDirectory": "test-results",
        "outputName": "junit.xml",
        "classNameTemplate": "{classname}",
        "titleTemplate": "{title}"
      }]
    ],
    "coverageReporters": ["text", "lcov", "html", "json-summary"]
  }
}
```
Install: `npm install --save-dev jest-junit`

### GitHub Actions — upload and display reports

Add these steps to each test job in `.github/workflows/tests.yml`:

```yaml
- name: Publish test results
  uses: dorny/test-reporter@v1
  if: always()
  with:
    name: '${{ matrix.project }} Test Results'
    path: 'playwright-results/results.xml,test-results/junit.xml'
    reporter: java-junit

- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: playwright-report-${{ matrix.project }}
    path: playwright-report/
    retention-days: 14
```

### Allure report (if allure-playwright / allure-jest installed)

Add to CI after all test jobs complete:

```yaml
allure-report:
  name: Generate Allure Report
  needs: [unit, integration, e2e]
  if: always()
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/download-artifact@v4
      with:
        pattern: allure-results-*
        merge-multiple: true
        path: allure-results/
    - uses: simple-elf/allure-report-action@master
      with:
        allure_results: allure-results
        allure_report: allure-report
        gh_pages: gh-pages
        allure_history: allure-history
    - uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_branch: gh-pages
        publish_dir: allure-history
```

### Jenkins — JUnit and HTML publishers

Add to each parallel stage's `post { always { … } }`:
```groovy
junit 'test-results/**/*.xml'
publishHTML(target: [
  allowMissing: false,
  alwaysLinkToLastBuild: true,
  keepAll: true,
  reportDir: 'playwright-report',
  reportFiles: 'index.html',
  reportName: 'Playwright Report',
])
```

## Test result retention policy

Recommend retention based on test type:
- Unit test JUnit XML: 30 days (small, cheap to store)
- E2E HTML reports: 14 days (larger)
- Allure history: indefinite on `gh-pages` branch (enables trend graphs)
- Video/trace artifacts (Playwright): 7 days, only on failure

Add `retention-days:` to every `upload-artifact` step.

## Output

1. Updated `playwright.config.ts` reporter array
2. Updated `jest.config.ts` reporters
3. Updated CI config with report upload and Allure steps

After writing, print a summary of what reporters were added and where reports will be published.
