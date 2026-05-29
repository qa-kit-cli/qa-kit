---
command: qakit.write.vitest
description: Write Vitest unit tests for Vite-based projects with vi.mock and inline snapshots.
---

# /qakit.write.vitest

Write Vitest unit tests for the specified module or component.

## Context

**Input:** $ARGUMENTS
*(Provide the module or component path. Example: "src/composables/useCart.ts" or "src/components/PriceTag.vue".)*

Before writing, read:
- `.qakit/memory/test-policy.md` — coverage thresholds
- `.qakit/memory/test-plan.md` — TC-NNN IDs and target paths
- The source file at `$ARGUMENTS`

Confirm Vitest is installed: check `package.json` for `"vitest"` and `vite.config.*` for the test config block.

## Conventions (mandatory)

**Imports**
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
```
Never mix `jest` and `vi` APIs — they are not interchangeable.

**Mocking**
```typescript
// Hoist vi.mock calls — they are automatically hoisted to the top
vi.mock('../api/cart', () => ({
  fetchCart: vi.fn(),
}));

// Factory mock with a spy
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Cleanup
beforeEach(() => vi.clearAllMocks());
afterAll(() => vi.unstubAllGlobals());
```

**Composable / hook tests**
```typescript
import { mount } from '@vue/test-utils'; // Vue
// or
import { renderHook, act } from '@testing-library/react'; // React

it('TC-NNN increments quantity', () => {
  const { result } = renderHook(() => useCart());
  act(() => result.current.addItem({ id: '1', qty: 1 }));
  expect(result.current.totalItems).toBe(1);
});
```

**Inline snapshots** — use for stable, readable assertions on small objects:
```typescript
expect(formatPrice(1234.5, 'USD')).toMatchInlineSnapshot(`"$1,234.50"`);
```
Use `toMatchSnapshot()` for larger structures that are maintained in snapshot files.

**Table-driven tests**
```typescript
it.each([
  { input: 0, expected: '$0.00' },
  { input: 1000, expected: '$1,000.00' },
  { input: -1, expected: 'Invalid' },
])('TC-NNN formatPrice($input) → $expected', ({ input, expected }) => {
  expect(formatPrice(input, 'USD')).toBe(expected);
});
```

**Timer fakes**
```typescript
vi.useFakeTimers();
// ... trigger debounced/throttled logic
vi.runAllTimers();
expect(spy).toHaveBeenCalledOnce();
vi.useRealTimers();
```

## What to write

For the module at `$ARGUMENTS`:
1. **Unit tests** for every exported function or composable — mock all side effects
2. **Snapshot tests** for pure render functions or formatters
3. **Async tests** for any function returning a Promise — test both resolved and rejected paths
4. **Timer / interval tests** if the module uses `setTimeout`, `setInterval`, or `debounce`

Target coverage: meet the unit threshold from `test-policy.md` for this file.

## Output

Co-located test: `<same dir>/<module>.test.ts`
Or: `src/__tests__/<module>.test.ts`

After writing, print: `Added N tests (TC-NNN through TC-NNN) in <path>`
