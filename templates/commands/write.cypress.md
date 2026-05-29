---
command: qakit.write.cypress
description: Write Cypress TypeScript E2E and component tests.
---

# /qakit.write.cypress

Write Cypress TypeScript tests for the specified feature or component.

## Context

**Input:** $ARGUMENTS
*(Provide the feature, user journey, or component path. Example: "user login flow" or "src/components/LoginForm.tsx".)*

Before writing, read:
- `.qakit/memory/test-plan.md` — target paths, TC-NNN IDs, and pyramid targets
- `.qakit/memory/test-policy.md` — approved Cypress version and conventions
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases

Also read the source file(s) to understand the component's props, events, and API interactions.

## Conventions (mandatory)

**Imports and setup**
```typescript
// cypress/support/commands.ts — add custom commands there, not inline
import './commands';
```

**Selectors** — prefer in this order:
1. `cy.findByRole('button', { name: 'Submit' })` — via `@testing-library/cypress`
2. `cy.get('[data-testid="submit-btn"]')` — stable data-testid attribute
3. Never use CSS class names or `nth-child` selectors

**Intercepts before action**
```typescript
cy.intercept('POST', '/api/checkout', { fixture: 'checkout-success.json' }).as('checkout');
cy.get('[data-testid="submit"]').click();
cy.wait('@checkout').its('request.body').should('deep.equal', { … });
```
Always define `cy.intercept()` before the action that triggers the request.

**Test structure**
```typescript
describe('TC-NNN [Journey name]', () => {
  beforeEach(() => {
    cy.fixture('user').then((user) => cy.login(user)); // use custom commands for auth
    cy.visit('/checkout');
  });

  it('TC-NNN should <expected outcome>', () => {
    // Arrange → Act → Assert
  });
});
```

**Component tests** (Cypress component testing)
```typescript
import { mount } from 'cypress/react18';
import { LoginForm } from './LoginForm';

it('TC-NNN renders validation error for empty email', () => {
  mount(<LoginForm onSubmit={cy.stub()} />);
  cy.findByRole('button', { name: 'Sign in' }).click();
  cy.findByRole('alert').should('contain', 'Email is required');
});
```

**Fixtures**
- Store fixtures in `cypress/fixtures/<feature>/`
- Never hardcode test data inline; use `cy.fixture()` or `cy.task()` for dynamic data

**TC-NNN IDs** — assign from `test-plan.md` sequence.

## What to write

For the target in `$ARGUMENTS`:
1. **E2E happy path** — full user journey with real navigation
2. **Component tests** — if `$ARGUMENTS` references a component file, write component-level tests for its props and events
3. **Intercept-based error test** — stub a 500 response and verify graceful error handling

## Output

Save to `cypress/e2e/<feature>/<journey>.cy.ts` or `src/<component>/<Component>.cy.tsx` for component tests.
After writing, print: `Added N tests (TC-NNN through TC-NNN) in <path>`
