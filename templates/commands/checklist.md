---
command: qakit.checklist
description: Generate a QA readiness checklist for a feature or release.
---

# /qakit.checklist

Generate a QA readiness checklist.

Read `.qakit/memory/test-plan.md`, `.qakit/memory/test-policy.md`, and `.qakit/memory/qa-strategy.md`, then generate a QA readiness checklist for the upcoming feature or release.

## Output format

Save the checklist to `.qakit/memory/qa-checklist.md`:

```markdown
# QA Readiness Checklist — [Feature/Release Name]

## Test Coverage
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] E2E tests written and passing
- [ ] Accessibility tests passing (WCAG 2.1 AA)
- [ ] Visual regression baseline updated

## Documentation
- [ ] Test plan updated
- [ ] Traceability matrix updated
- [ ] Known issues documented

## Environments
- [ ] Staging environment verified
- [ ] Test data seeded
- [ ] Feature flags configured correctly

## CI/CD
- [ ] All CI pipelines passing
- [ ] Coverage threshold met (≥ policy minimum)
- [ ] No flaky tests in P0/P1 suite

## Sign-off
- [ ] QA lead sign-off
- [ ] Product owner reviewed test results
- [ ] Security review complete (if applicable)
```

## Rules

- Tailor checklist items to the actual scope and risk of the feature.
- Mark items that are already complete based on existing context files.
- Flag blockers with [BLOCKED] tags.
- Note which items require manual QA vs automated checks.

$ARGUMENTS
