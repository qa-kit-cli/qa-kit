# /qakit.maintain.upgrade

Upgrade a test suite from one framework version to another.

## Description

Guides and executes a framework version upgrade: updates `package.json` dependencies, migrates deprecated APIs to their replacements, updates `playwright.config.ts` / `jest.config.ts` / `cypress.config.ts` for the new version, fixes any breaking changes in test files, and regenerates visual baselines if Playwright screenshots were affected.

## Usage

```
/qakit.maintain.upgrade <framework> <from-version> <to-version>
```

## Arguments

- `<framework>` — `playwright`, `cypress`, `jest`, `vitest`, or `selenium`
- `<from-version>` and `<to-version>` — version strings, e.g. `1.40` `1.50`

## Reads from memory

- `.qakit/memory/test-policy.md` — approved framework versions; blocks downgrades below minimums
- `package.json` and config files — current version and configuration

## Produces

- Updated `package.json` `devDependencies`
- Migrated config file (`playwright.config.ts`, etc.)
- Updated test files where breaking API changes apply
- Inline changelog of every API change made

## Example

```
/qakit.maintain.upgrade playwright 1.44 1.50
```

Common Playwright 1.44 → 1.50 changes handled:
- `page.locator('…')` → `page.getByRole('…')` where applicable
- Deprecated `waitForNavigation` → `page.waitForURL`
- `expect(page).toHaveURL` parameter type changes

## Related commands

- `/qakit.maintain.refactor` — bring tests into compliance with updated conventions post-upgrade
- `/qakit.write.visual` — regenerate visual baselines after a Playwright upgrade
