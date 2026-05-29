# /qakit.write.vitest

Write Vitest unit tests for Vite-based projects.

## Description

Generates Vitest test files using `vi.mock()`, `vi.spyOn()`, and inline snapshots. Designed for Vite-based projects (Vue, React + Vite, SvelteKit). Uses native ESM and Vitest's built-in `jsdom` or `happy-dom` environment.

## Usage

```
/qakit.write.vitest <module or component>
```

## Arguments

- Path to the source module or component to test
- Examples: `src/stores/cartStore.ts`, `src/components/ProductCard.vue`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs and target test paths
- `.qakit/memory/test-policy.md` — coverage thresholds, approved test environment (`jsdom` vs `happy-dom`)

## Produces

A `*.test.ts` (or `*.spec.ts`) file at the path specified in `test-plan.md`.

Conventions applied:
- `import { describe, it, expect, vi } from 'vitest'`
- `vi.mock('../module', () => ({ … }))` for dependency mocking
- `vi.useFakeTimers()` for time-dependent logic
- `expect(result).toMatchInlineSnapshot(…)` for structured output

## Example

```
/qakit.write.vitest src/composables/useAuth.ts
```

## Related commands

- `/qakit.write.jest` — use instead for non-Vite (CRA, Next.js, Node) projects
- `/qakit.write.fixtures` — generate shared test data factories
