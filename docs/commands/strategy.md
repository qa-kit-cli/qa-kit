# /qakit.strategy

Generate a complete QA strategy document for a feature or project.

## Description

Analyses a feature specification and produces `.qakit/memory/qa-strategy.md` — the primary planning document for the QA cycle. Covers risk classification, user journeys, test types, acceptance criteria, data requirements, environment setup, edge cases, and open questions.

Run this first when starting QA for a new feature. All other commands (testplan, write.*, ci.*) read from the output of this command.

## Usage

```
/qakit.strategy <input>
```

## Arguments

Paste any of the following as `<input>`:
- A feature specification or PRD
- A Jira ticket URL or ticket text
- A plain-English description of the feature
- *(empty)* — analyses the current working directory (README, `src/`, recent git diff)

## Reads from memory

- `.qakit/memory/test-policy.md` — coverage thresholds, approved frameworks, environment matrix

## Produces

`.qakit/memory/qa-strategy.md` — created or updated in place.

## Example

```
/qakit.strategy Add OAuth 2.0 login with Google and GitHub. Users can link multiple providers to one account. Session expires after 24h of inactivity.
```

## Related commands

- `/qakit.testplan` — produces a test plan from this strategy
- `/qakit.clarify` — resolves open questions in the strategy before planning
- `/qakit.policy` — creates or updates `test-policy.md` (run before strategy on a new project)
