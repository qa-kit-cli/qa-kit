# /qakit.policy

Create or update `test-policy.md` — the QA governance document for this project.

## Description

Generates or refreshes `.qakit/memory/test-policy.md`, the authoritative governance document that all other QA Kit commands read to enforce standards. Covers coverage thresholds, approved frameworks, browser matrix, test organisation rules, flakiness policy, defect severity taxonomy, and CI/CD gates.

Run this once when setting up a new project, or when governance requirements change (new framework adopted, coverage threshold adjusted, etc.).

## Usage

```
/qakit.policy [<context>]
```

## Arguments

Optional `<context>`:
- Project constraints (e.g. `"Playwright only, no Cypress, 80% unit coverage required"`)
- Regulatory requirements (e.g. `"WCAG 2.1 AA mandatory on all P1 pages"`)
- *(empty)* — generates a policy from sensible defaults

## Reads from memory

- `.qakit/memory/test-policy.md` — if it exists, updates in place rather than replacing

## Produces

`.qakit/memory/test-policy.md` with sections: Coverage Thresholds, Approved Frameworks, Environment Matrix, Test Organisation, Flakiness Policy, Defect Severity Taxonomy, CI/CD Gates.

## Example

```
/qakit.policy We use Playwright for E2E and Jest for unit tests. Minimum 80% line coverage. All P1 pages must pass WCAG 2.1 AA. No Selenium — we're migrating away from it.
```

## Related commands

- `/qakit.strategy` — reads `test-policy.md` when generating the strategy
- `/qakit.testplan` — validates the plan against `test-policy.md`
