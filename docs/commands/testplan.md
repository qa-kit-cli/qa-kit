# /qakit.testplan

Produce a structured test plan from an existing QA strategy.

## Description

Reads `.qakit/memory/qa-strategy.md` and `.qakit/memory/test-policy.md`, then generates `.qakit/memory/test-plan.md`. The test plan defines scope, pyramid ratio, directory layout, environment matrix, data model, and CI/CD gates.

All `/qakit.write.*` and `/qakit.ci.*` commands read the test plan to get TC-NNN IDs, target file paths, and browser targets. Run this after `/qakit.strategy`.

## Usage

```
/qakit.testplan [<overrides>]
```

## Arguments

Optional `<overrides>`:
- `"focus on E2E only"` — skips unit and integration sections
- `"add performance section"` — includes load test planning
- *(empty)* — infers everything from `qa-strategy.md` and `test-policy.md`

## Reads from memory

- `.qakit/memory/qa-strategy.md` — user journeys, acceptance criteria, test types
- `.qakit/memory/test-policy.md` — coverage thresholds, approved frameworks, CI gates

## Produces

`.qakit/memory/test-plan.md` with sections: Summary, Technical Context, Policy Check, Test Architecture (pyramid), Suite Layout, Environment Matrix, Data Model, CI/CD Integration.

## Example

```
/qakit.testplan
```

## Related commands

- `/qakit.strategy` — run first to create the strategy
- `/qakit.coverage` — validates existing tests against this plan
- `/qakit.write.playwright` — writes tests using this plan's TC-NNN IDs and paths
