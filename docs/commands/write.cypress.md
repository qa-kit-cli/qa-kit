# /qakit.write.cypress

Write Cypress TypeScript E2E or component tests.

## Description

Generates Cypress TypeScript test files using `cy.intercept`, `cy.fixture`, and Cypress Cloud conventions. Applies TC-NNN IDs from the test plan and follows the approved locator strategy and flakiness rules in `test-policy.md`.

Supports both Cypress E2E (`cypress/e2e/`) and Component Testing (`cypress/component/`).

## Usage

```
/qakit.write.cypress <feature or component>
```

## Arguments

- Feature, user journey name, or path to the component under test
- Examples: `"shopping cart add/remove"`, `src/components/CartWidget.tsx`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs and target paths for this journey
- `.qakit/memory/test-policy.md` — locator rules, retry settings, Cypress Cloud config
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases

## Produces

A `*.cy.ts` file at the path specified in `test-plan.md`.

Conventions applied:
- `cy.intercept()` for API mocking — no real network in unit/component tests
- `cy.fixture()` for test data — no hardcoded IDs
- `cy.findByRole()` / `cy.findByLabelText()` via `@testing-library/cypress`
- `cy.wait('@alias')` — never `cy.wait(N)` with a static delay

## Example

```
/qakit.write.cypress TC-005 add to cart flow — src/pages/ProductPage.tsx
```

## Related commands

- `/qakit.write.pom` — generate POM classes for reusable page interactions
- `/qakit.write.fixtures` — generate `cy.fixture()` data files
- `/qakit.maintain.upgrade` — upgrade Cypress to a new major version
