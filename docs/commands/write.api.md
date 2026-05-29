# /qakit.write.api

Write API contract tests for REST or GraphQL endpoints.

## Description

Generates API contract tests using Playwright's `APIRequestContext` (for projects already using Playwright) or Supertest (for pure Node.js backends). Tests verify request/response schemas, status codes, error formats, and authentication requirements.

## Usage

```
/qakit.write.api <endpoint or resource>
```

## Arguments

- API endpoint path, resource name, or OpenAPI spec file path
- Examples: `"POST /api/auth/login"`, `"order resource"`, `openapi.yaml`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs for API tests, target file paths
- `.qakit/memory/qa-strategy.md` — API contracts and edge cases from the strategy

## Produces

`tests/integration/<resource>.api.test.ts` (Supertest) or `tests/api/<resource>.spec.ts` (Playwright).

Example (Playwright APIRequestContext):
```typescript
test('TC-030 POST /api/login returns 200 with valid credentials', async ({ request }) => {
  const response = await request.post('/api/login', {
    data: { email: 'verified@example.com', password: 'Test1234!' },
  });
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toMatchObject({ token: expect.any(String), expiresIn: 86400 });
});
```

Covers: happy path, invalid credentials (401), missing fields (422), rate limit (429), auth-required endpoints (403 without token).

## Example

```
/qakit.write.api POST /api/auth/login POST /api/auth/refresh DELETE /api/auth/session
```

## Related commands

- `/qakit.write.playwright` — browser-level tests that exercise the same endpoints
- `/qakit.write.jest` — unit tests for request validation logic
