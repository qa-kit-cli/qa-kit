# /qakit.review.bugreport

Generate a structured bug report with repro steps, severity, expected/actual, and Jira formatting.

## Description

Takes a description of a defect (from test failure output, manual testing, or a user report) and produces a fully structured bug report following the `bug-report-template.md` format: ID, severity (P0–P3), environment details, steps to reproduce, expected vs. actual result, evidence links, root cause hypothesis, and suggested fix.

If the `jira` extension is enabled and `JIRA_URL` is set, also outputs a Jira-compatible create URL.

## Usage

```
/qakit.review.bugreport <defect description>
```

## Arguments

- Description of the defect, pasted test failure output, or steps observed
- Examples: `"Login returns 500 when Redis is down"`, paste from Playwright test failure log

## Reads from memory

- `.qakit/memory/test-policy.md` — severity taxonomy (P0/P1/P2/P3 definitions)
- `.qakit/memory/test-plan.md` — links to the TC-NNN test case that caught the defect

## Produces

A fully formatted bug report printed inline, ready to copy into Jira or GitHub Issues. Fields populated:
- ID, Severity, Priority, Status, Reporter, Date
- Environment (version, browser, OS, test env)
- Steps to Reproduce (numbered)
- Expected vs. Actual result
- Evidence section (placeholders for screenshot/trace/log)
- Root cause hypothesis
- Suggested fix

## Example

```
/qakit.review.bugreport Submitting the login form with valid credentials returns HTTP 500. Only reproducible when Redis is unreachable. Observed in staging. Test TC-003 catches this.
```

## Related commands

- `/qakit.review.pr` — review the PR that introduced the defect
- `/qakit.write.playwright` — write a regression test to prevent recurrence
