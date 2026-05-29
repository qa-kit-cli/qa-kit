# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities.

Instead, report them privately via GitHub's Security Advisory feature:
https://github.com/qa-kit/qa-kit/security/advisories/new

We aim to respond within 72 hours and release a patch within 14 days for confirmed vulnerabilities.

## Scope

- CLI command injection via user-controlled inputs
- Token/credential exposure in generated files or logs
- Extension/preset manifest validation bypasses
- Catalog URL spoofing / supply chain issues

## Out of Scope

- Vulnerabilities in generated test code (responsibility of the consuming project)
- Issues in third-party AI agents
