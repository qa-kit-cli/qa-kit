---
command: qakit.write.cypress
description: Write Cypress TypeScript tests — E2E and component (Cypress preset).
---

# /qakit.write.cypress

Write Cypress TypeScript tests for the specified feature or component.

## Context

**Input:** $ARGUMENTS
*(Feature, journey, or component path. Example: "user login flow" or "src/components/LoginForm.tsx".)*

Read before writing:
- `.qakit/memory/test-plan.md` — TC-NNN IDs, target paths
- `.qakit/memory/test-policy.md` — approved Cypress version and conventions
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases
- `cypress.config.ts` — `baseUrl`, `specPattern`, component testing framework

## cypress.config.ts alignment

Check `cypress.config.ts` before writing. Create it if absent:

```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: process.env.BASE_URL ?? 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
    viewportWidth: 1280,
    viewportHeight: 720,
    retries: { runMode: 2, openMode: 0 },
    video: false,
    screenshotOnRunFailure: true,
  },
  component: {
    devServer: { framework: 'react', bundler: 'vite' },  // adjust for Vue/Angular/Next
    specPattern: 'src/**/*.cy.{ts,tsx}',
    supportFile: 'cypress/support/component.ts',
  },
});
```

## E2E conventions

**Selectors — strict priority:**
1. `cy.findByRole('button', { name: 'Place order' })` via `@testing-library/cypress`
2. `cy.get('[data-testid="submit"]')` — stable data attribute
3. Never: CSS class names, IDs that look auto-generated, positional selectors

Install `@testing-library/cypress` if not present:
```bash
npm install --save-dev @testing-library/cypress
# cypress/support/commands.ts:
import '@testing-library/cypress/add-commands';
```

**Intercept before action — always:**
```typescript
cy.intercept('POST', '/api/orders', { fixture: 'orders/success.json' }).as('placeOrder');
cy.findByRole('button', { name: 'Place order' }).click();
cy.wait('@placeOrder').its('request.body').should('deep.include', { productId: 'prod_001' });
```

**Session caching (Cypress 12+):**
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('loginAs', (role: 'admin' | 'user') => {
  cy.session(
    [`user-${role}`],
    () => {
      cy.visit('/login');
      cy.findByLabelText('Email').type(Cypress.env(`${role}Email`));
      cy.findByLabelText('Password').type(Cypress.env(`${role}Password`));
      cy.findByRole('button', { name: 'Sign in' }).click();
      cy.url().should('include', '/dashboard');
    },
    { cacheAcrossSpecs: true },
  );
});
```

**Test structure:**
```typescript
describe('TC-NNN Checkout — payment step', () => {
  beforeEach(() => {
    cy.loginAs('user');
    cy.visit('/checkout');
  });

  it('TC-NNN completes order with valid Visa card', () => {
    cy.intercept('POST', '/api/orders', { fixture: 'orders/success.json' }).as('placeOrder');

    cy.findByLabelText('Card number').type('4242424242424242');
    cy.findByLabelText('Expiry').type('12/28');
    cy.findByLabelText('CVV').type('123');
    cy.findByRole('button', { name: 'Place order' }).click();

    cy.wait('@placeOrder').its('response.statusCode').should('eq', 201);
    cy.findByRole('heading', { name: /order confirmed/i }).should('be.visible');
    cy.url().should('match', /\/orders\/ord_/);
  });

  it('TC-NNN shows error on card decline', () => {
    cy.intercept('POST', '/api/orders', { statusCode: 402, fixture: 'orders/declined.json' }).as('decline');

    cy.findByLabelText('Card number').type('4000000000000002');
    cy.findByRole('button', { name: 'Place order' }).click();

    cy.wait('@decline');
    cy.findByRole('alert').should('contain.text', 'Your card was declined');
  });
});
```

## Component testing

For components referenced in `$ARGUMENTS`:

```typescript
// src/components/CheckoutForm.cy.tsx
import { mount } from 'cypress/react18';
import { CheckoutForm } from './CheckoutForm';

describe('TC-NNN CheckoutForm component', () => {
  it('TC-NNN renders validation error when submitted empty', () => {
    const onSubmit = cy.stub().as('onSubmit');
    mount(<CheckoutForm onSubmit={onSubmit} />);

    cy.findByRole('button', { name: 'Place order' }).click();

    cy.findByRole('alert').should('contain.text', 'Card number is required');
    cy.get('@onSubmit').should('not.have.been.called');
  });

  it('TC-NNN calls onSubmit with card data on valid input', () => {
    const onSubmit = cy.stub().as('onSubmit');
    mount(<CheckoutForm onSubmit={onSubmit} />);

    cy.findByLabelText('Card number').type('4242424242424242');
    cy.findByLabelText('Expiry').type('12/28');
    cy.findByLabelText('CVV').type('123');
    cy.findByRole('button', { name: 'Place order' }).click();

    cy.get('@onSubmit').should('have.been.calledWith',
      Cypress.sinon.match({ cardNumber: '4242424242424242' })
    );
  });
});
```

## Fixtures

Store fixtures in `cypress/fixtures/<feature>/`:
- `orders/success.json` — 201 order response
- `orders/declined.json` — 402 card decline response
- `users/standard.json` — standard user object

Never hardcode test data inline; always use `cy.fixture()` or `cy.task()`.

## TC-NNN IDs

Assign the next available IDs from `test-plan.md`.

## Output

E2E: `cypress/e2e/<feature>/<journey>.cy.ts`
Component: `src/<component>/<Component>.cy.tsx`

After writing: `Added N tests (TC-NNN through TC-NNN) in <path>`
