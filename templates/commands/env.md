---
command: qakit.env
description: Define test environments, browser/device matrix, data rules, and service virtualization.
---

# /qakit.env

Define test environments and data rules.

Read `.qakit/memory/test-plan.md` and `.qakit/memory/qa-strategy.md`, then define the full test environment specification.

## Output format

Save to `.qakit/memory/test-environments.md`:

```markdown
# Test Environments

## Environments

### Local
- Purpose: Developer unit/integration tests
- URL: http://localhost:3000
- Data: Local seed data (scripts/seed-local.sql)
- Auth: Dev credentials in .env.local
- Reset: `npm run db:reset`

### Staging
- Purpose: E2E, UAT, performance testing
- URL: https://staging.example.com
- Data: Anonymized production snapshot, refreshed nightly
- Auth: staging-qa@example.com / [in secrets manager]
- Reset: Contact DevOps

### Production (read-only monitoring)
- Purpose: Smoke tests post-deploy
- URL: https://example.com
- Data: Real data — read-only assertions only
- Auth: Dedicated monitoring account

## Browser and Device Matrix

| Browser | Version | OS | Priority |
|---------|---------|-----|----------|
| Chrome | Latest | Windows 11 | P0 |
| Safari | Latest | macOS 14 | P0 |
| Firefox | Latest | Windows 11 | P1 |
| Chrome Mobile | Latest | Android 14 | P1 |
| Safari Mobile | Latest | iOS 17 | P1 |
| Edge | Latest | Windows 11 | P2 |

## Test Data Rules
- Never use real PII in tests.
- Seed data must be deterministic and version-controlled.
- Tests must clean up created data after execution.
- Secrets must be retrieved from the secrets manager — never hardcoded.

## Third-party Dependencies
| Service | Stub / Real | Notes |
|---------|-------------|-------|
| Payment gateway | Stub (Stripe test mode) | Use test card 4242 4242 4242 4242 |
| Email service | Mailhog (local), real (staging) | |
| Feature flags | LaunchDarkly test environment | |

## Service Virtualization
- [List any WireMock or Prism stubs in use]

## Secrets Management
- Local: .env.local (gitignored)
- CI: GitHub Actions secrets
- Staging: AWS Secrets Manager
```

## Rules

- Define all environments where tests will run.
- Specify data rules that prevent PII leakage and test pollution.
- Call out third-party dependencies that need stubs in test environments.
- Include instructions for resetting each environment to a known state.

$ARGUMENTS
