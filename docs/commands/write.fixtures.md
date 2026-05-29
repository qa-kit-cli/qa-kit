# /qakit.write.fixtures

Generate test fixtures, factory functions, and seed data for a test suite.

## Description

Creates reusable test data infrastructure: factory functions that generate typed test objects, static JSON fixtures, and database seed scripts. All fixture data uses `@example.com` addresses and synthetic values — no real PII.

Run this early in the setup phase before writing E2E or integration tests that need seeded state.

## Usage

```
/qakit.write.fixtures <entity or domain>
```

## Arguments

- Entity or domain name(s) to generate fixtures for
- Examples: `"user"`, `"order product"`, `"auth session"`

## Reads from memory

- `.qakit/memory/test-plan.md` — Data Model section; fixture names and relationships
- `.qakit/memory/qa-strategy.md` — Data Requirements section; PII constraints

## Produces

Files in `tests/fixtures/`:
- `<entity>.ts` — factory function with typed overrides parameter
- `<entity>.json` — static fixture JSON for simple cases
- `seed-<domain>.ts` — idempotent DB seed script (if the plan specifies real DB tests)

Example factory:
```typescript
export function createUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    email: `user-${Date.now()}@example.com`,
    role: 'member',
    ...overrides,
  };
}
```

## Example

```
/qakit.write.fixtures user order
```

## Related commands

- `/qakit.write.playwright` — imports these factories in `test.beforeEach`
- `/qakit.write.jest` — imports factories for unit test input data
- `/qakit.maintain.data` — audits fixtures for orphaned or hardcoded values
