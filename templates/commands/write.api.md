---
command: qakit.write.api
description: Write API contract tests (REST/GraphQL) using Supertest or Playwright APIRequestContext.
---

# /qakit.write.api

Write API contract tests for the specified endpoint or service.

## Context

**Input:** $ARGUMENTS
*(Provide the API route, service file, or OpenAPI spec path. Example: "POST /api/checkout" or "src/api/orders.ts" or "openapi.yml".)*

Before writing, read:
- `.qakit/memory/test-plan.md` — TC-NNN IDs for API tests
- `.qakit/memory/test-policy.md` — approved API testing framework

Detect the project stack:
- **Node.js/Express/Fastify:** use Supertest
- **Next.js API routes:** use Supertest or `@playwright/test` APIRequestContext
- **Any stack, black-box:** use Playwright APIRequestContext
- **GraphQL:** use Supertest or Apollo testing utilities

If an OpenAPI / Swagger spec exists at `$ARGUMENTS` or in the project root, generate tests from the schema.

## Supertest (Node.js)

```typescript
import request from 'supertest';
import { app } from '../../src/app';
import { db } from '../../src/db';

beforeAll(async () => db.connect());
afterAll(async () => db.disconnect());
beforeEach(async () => db.seed());
afterEach(async () => db.cleanup());

describe('TC-NNN POST /api/orders', () => {
  it('TC-NNN 201 — creates order with valid payload', async () => {
    const response = await request(app)
      .post('/api/orders')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ productId: 'prod_001', quantity: 2 });

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      id: expect.stringMatching(/^ord_/),
      status: 'pending',
      total: expect.any(Number),
    });
  });

  it('TC-NNN 400 — rejects order with missing productId', async () => {
    const response = await request(app)
      .post('/api/orders')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ quantity: 1 });

    expect(response.status).toBe(400);
    expect(response.body.errors).toContainEqual(
      expect.objectContaining({ field: 'productId', code: 'required' }),
    );
  });

  it('TC-NNN 401 — rejects unauthenticated request', async () => {
    const response = await request(app).post('/api/orders').send({ productId: 'prod_001' });
    expect(response.status).toBe(401);
  });

  it('TC-NNN 409 — returns conflict for duplicate idempotency key', async () => {
    const key = 'idem_test_001';
    await request(app).post('/api/orders').set('Idempotency-Key', key).send(validPayload);
    const response = await request(app).post('/api/orders').set('Idempotency-Key', key).send(validPayload);
    expect(response.status).toBe(409);
  });
});
```

## Playwright APIRequestContext (framework-agnostic, black-box)

```typescript
import { test, expect } from '@playwright/test';

test.describe('TC-NNN POST /api/orders — contract tests', () => {
  test('TC-NNN 201 with valid payload', async ({ request }) => {
    const response = await request.post('/api/orders', {
      headers: { Authorization: `Bearer ${process.env.TEST_TOKEN}` },
      data: { productId: 'prod_001', quantity: 2 },
    });
    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.id).toMatch(/^ord_/);
  });
});
```

## Schema validation

When an OpenAPI spec is available, validate every response body against the schema:

```typescript
import Ajv from 'ajv';
import schema from '../../openapi.json';

const ajv = new Ajv();
const validate = ajv.compile(schema.components.schemas.Order);

it('TC-NNN response matches Order schema', async () => {
  const response = await request(app).post('/api/orders').send(validPayload);
  const valid = validate(response.body);
  expect(valid).toBe(true);
  expect(validate.errors).toBeNull();
});
```

## What to write

For the endpoint(s) in `$ARGUMENTS`:
1. **Happy path** — 2xx response, response body shape validated
2. **Validation errors** — 400 for every required field, every invalid format
3. **Auth tests** — 401 (no token), 403 (insufficient role)
4. **Not found** — 404 for non-existent resource IDs
5. **Idempotency** — 409 for duplicate keys where the API supports them
6. **Rate limiting** — 429 if applicable
7. **Schema compliance** — response body matches OpenAPI schema if spec exists

## Output

`tests/api/<resource>.api.test.ts` or `tests/integration/<endpoint>.test.ts`

After writing, print: `Added N API tests (TC-NNN through TC-NNN) in <path>`
