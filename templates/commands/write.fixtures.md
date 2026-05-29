---
command: qakit.write.fixtures
description: Generate test fixtures, factory functions, and seed data for a test suite.
---

# /qakit.write.fixtures

Generate test fixtures, factory functions, and seed scripts for the specified test area.

## Context

**Input:** $ARGUMENTS
*(Provide the feature area or data domain. Example: "user account fixtures", "product catalogue seed data", or "checkout flow test data".)*

Before writing, read:
- `.qakit/memory/test-plan.md` — Data Model section for fixture strategy (static JSON, factories, seeded DB)
- `.qakit/memory/qa-strategy.md` — Data Requirements section for PII rules and environment constraints
- `.qakit/memory/test-policy.md` — approved fixture approach

Scan existing `tests/fixtures/` or `cypress/fixtures/` for patterns already in use — extend, do not duplicate.

## Fixture types to generate

### 1. Static JSON fixtures (for API mocks and simple entities)

```json
// tests/fixtures/user/standard-user.json
{
  "id": "usr_001",
  "email": "test+standard@example.com",
  "role": "user",
  "plan": "free",
  "emailVerified": true
}
```

Name files descriptively: `<entity>/<variant>.json` — e.g., `user/admin.json`, `user/unverified.json`.

Never use real PII. Use `example.com` emails, fictional names, fake card numbers (Stripe test cards: `4242 4242 4242 4242`).

### 2. Factory functions (for dynamic, parameterised data)

```typescript
// tests/factories/userFactory.ts
import { faker } from '@faker-js/faker';

export interface UserData {
  id: string;
  email: string;
  role: 'admin' | 'user' | 'readonly';
  plan: 'free' | 'pro' | 'enterprise';
}

export function createUser(overrides: Partial<UserData> = {}): UserData {
  return {
    id: `usr_${faker.string.nanoid(8)}`,
    email: faker.internet.email({ provider: 'example.com' }),
    role: 'user',
    plan: 'free',
    ...overrides,
  };
}

export function createAdmin(overrides: Partial<UserData> = {}): UserData {
  return createUser({ role: 'admin', plan: 'enterprise', ...overrides });
}
```

### 3. Playwright fixture composition (for shared setup)

```typescript
// tests/e2e/fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';

type Fixtures = { loggedInPage: LoginPage };

export const test = base.extend<Fixtures>({
  loggedInPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.loginAs({ email: 'test@example.com', password: 'Password1!' });
    await use(loginPage);
  },
});

export { expect } from '@playwright/test';
```

### 4. Database seed scripts (for integration/E2E suites with a real DB)

```typescript
// tests/seed/seedCheckoutData.ts
export async function seedCheckoutScenario(db: Database): Promise<void> {
  await db.users.create({ id: 'usr_checkout_001', email: 'checkout@example.com' });
  await db.products.createMany([
    { id: 'prod_001', name: 'Test Widget', price: 999, stock: 10 },
  ]);
}

export async function cleanupCheckoutData(db: Database): Promise<void> {
  await db.orders.deleteMany({ where: { userId: 'usr_checkout_001' } });
  await db.users.delete({ where: { id: 'usr_checkout_001' } });
}
```

Always provide a cleanup function alongside every seed function.

## What to generate

For the area in `$ARGUMENTS`:
1. Static JSON fixtures for the entity types involved
2. Factory functions covering: default case, edge-case variants (empty, max-length, special characters), and each user role relevant to the feature
3. Playwright fixture composition if the project uses Playwright and shared auth is needed
4. Seed + cleanup functions if a real DB is used

## Output

- `tests/fixtures/<entity>/` — JSON files
- `tests/factories/<entity>Factory.ts` — factory functions
- `tests/e2e/fixtures.ts` — Playwright fixture extension (update if exists)
- `tests/seed/seed<Feature>.ts` — seed + cleanup (if DB required)

After writing, print a summary of what was created and how to use the factories.
