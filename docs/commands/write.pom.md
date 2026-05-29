# /qakit.write.pom

Generate Page Object Model (POM) classes for a set of pages or UI components.

## Description

Creates POM TypeScript classes that encapsulate page interactions, hiding implementation details (locators, navigation) behind a clean interface. Each POM class exposes named action methods (`goto()`, `fillForm()`, `submit()`) and assertion helpers (`expectError()`, `expectSuccess()`).

POM classes are placed in `tests/pages/` and imported by E2E test files, reducing duplication and improving maintainability.

## Usage

```
/qakit.write.pom <page or component list>
```

## Arguments

- Page name(s), route path(s), or component file path(s)
- Examples: `"login page"`, `src/pages/Checkout.tsx`, `"/cart /checkout /confirmation"`

## Reads from memory

- `.qakit/memory/test-policy.md` — approved locator strategy (must use `getByRole`/`getByLabel`)
- `.qakit/memory/test-plan.md` — which journeys use these pages

## Produces

One `<PageName>Page.ts` file per page in `tests/pages/`.

Example generated class:
```typescript
export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto() { await this.page.goto('/login'); }
  async fillCredentials(email: string, password: string) { … }
  async submit() { await this.page.getByRole('button', { name: 'Sign in' }).click(); }
  async expectError(msg: string) { await expect(this.page.getByRole('alert')).toContainText(msg); }
}
```

## Example

```
/qakit.write.pom src/pages/LoginPage.tsx src/pages/DashboardPage.tsx
```

## Related commands

- `/qakit.write.playwright` — uses these POM classes in test files
- `/qakit.write.cypress` — Cypress equivalent: `cypress/pages/` classes
