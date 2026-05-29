# /qakit.write.jest

Write Jest unit or integration tests with mocks, spies, and coverage annotations.

## Description

Generates Jest TypeScript test files targeting the module or function specified. Applies `jest.mock()`, `jest.spyOn()`, snapshot testing, and coverage annotations. Reads TC-NNN IDs from `test-plan.md`.

Use for unit testing business logic, service classes, utility functions, and React component rendering.

## Usage

```
/qakit.write.jest <module or function>
```

## Arguments

- Path to the source module, class, or function to test
- Examples: `src/services/AuthService.ts`, `src/utils/priceCalc.ts`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs for the unit layer, target file paths
- `.qakit/memory/test-policy.md` — coverage thresholds, approved mock strategy

## Produces

A `*.test.ts` file at the path specified in `test-plan.md`.

Conventions applied:
- `describe('ClassName', () => { it('TC-NNN should …', …) })`
- `jest.mock('../dependency')` for external dependencies
- `jest.spyOn(obj, 'method')` for partial mocks
- `expect(result).toMatchInlineSnapshot(…)` for complex output
- `@jest-environment node` annotation for non-DOM tests

## Example

```
/qakit.write.jest src/services/AuthService.ts
```

## Related commands

- `/qakit.write.vitest` — use instead for Vite-based projects
- `/qakit.write.fixtures` — generate factory functions for test data
- `/qakit.ci.github-actions` — configure coverage reporting in CI
