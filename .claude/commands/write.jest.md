---
command: qakit.write.jest
description: Write Jest unit and integration tests with mocks, spies, and coverage annotations.
---

# /qakit.write.jest

Write Jest unit or integration tests for the specified module or component.

## Context

**Input:** $ARGUMENTS
*(Provide the module path, function name, or component. Example: "src/utils/cartCalculator.ts" or "src/services/PaymentService.ts".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — coverage thresholds (unit line % and branch %)
- `.qakit/memory/test-plan.md` — TC-NNN IDs for this module and target file path
- The source file at `$ARGUMENTS` — understand the exports, dependencies, and edge cases

## Conventions (mandatory)

**Project setup inference**
Check `package.json` for Jest config (`"jest"` key or `jest.config.*`). Use `@jest/globals` if the project uses ESM; otherwise use globals from `@types/jest`.

**Import style**
```typescript
import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
// or
import { cartTotal } from '../cartCalculator';
```

**Mocking**
```typescript
// Module mock — at top of file, before imports
jest.mock('../paymentClient', () => ({
  charge: jest.fn(),
}));

// Spy on a method without replacing the module
const spy = jest.spyOn(service, 'sendEmail').mockResolvedValue(undefined);
```
Always clear mocks in `beforeEach`:
```typescript
beforeEach(() => jest.clearAllMocks());
```

**Test structure**
```typescript
describe('cartTotal', () => {
  describe('given an empty cart', () => {
    it('TC-NNN returns 0', () => {
      expect(cartTotal([])).toBe(0);
    });
  });

  describe('given items with discounts', () => {
    it.each([
      [100, 10, 90],
      [200, 50, 100],
    ])('TC-NNN price=%s discount=%s → total=%s', (price, discount, expected) => {
      expect(cartTotal([{ price, discount }])).toBe(expected);
    });
  });
});
```

**Async tests**
```typescript
it('TC-NNN resolves with confirmation ID on success', async () => {
  (chargeCard as jest.Mock).mockResolvedValue({ id: 'ch_123' });
  const result = await processPayment({ amount: 100 });
  expect(result.confirmationId).toBe('ch_123');
});

it('TC-NNN throws PaymentError on card decline', async () => {
  (chargeCard as jest.Mock).mockRejectedValue(new Error('card_declined'));
  await expect(processPayment({ amount: 100 })).rejects.toThrow('card_declined');
});
```

**Coverage annotations**
Add `/* istanbul ignore next */` only for unreachable platform-specific branches, never to hide real logic from coverage.

## What to write

For the module at `$ARGUMENTS`:
1. **Unit tests** — test every exported function in isolation; mock all I/O
2. **Boundary tests** — null, undefined, empty string, zero, MAX_SAFE_INTEGER where relevant
3. **Integration tests** — if `$ARGUMENTS` is a service class, test it against a real (in-memory) dependency where practical
4. **Error path tests** — every thrown error and rejected promise

Target: meet the unit coverage threshold in `test-policy.md` for this file.

## Output

Save to: `<same directory as source>/<module>.test.ts` (co-located) or `tests/unit/<path>.test.ts`.

After writing, print: `Added N tests (TC-NNN through TC-NNN) in <path>`
