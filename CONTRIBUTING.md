# Contributing to QA Kit

Thank you for your interest in contributing to QA Kit!

## Ways to Contribute

- **Bug reports** — Open an issue with reproduction steps
- **New slash commands** — Propose via issue before implementing
- **New presets** — Community presets welcome (see `presets/PUBLISHING.md`)
- **New extensions** — See `extensions/EXTENSION-DEVELOPMENT-GUIDE.md`
- **New AI agent integrations** — See `integrations/CONTRIBUTING.md`
- **Documentation improvements** — PRs welcome

## Development Setup

```bash
git clone https://github.com/qa-kit/qa-kit.git
cd qa-kit
uv sync --extra dev --extra test
uv run qakit --help
```

## Running Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
```

## Type Checking

```bash
uv run mypy src/
```

## Linting

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Testing Slash Commands

Slash commands must be tested in at least one real AI agent before a PR is merged.
Report your test results in a table in the PR description:

| Agent | Command | Result |
|-------|---------|--------|
| Claude Code | `/qakit.write.playwright` | ✅ Pass |

## Branch Naming

`<type>/<number>-<slug>`

Types: `feat/`, `fix/`, `docs/`, `community/`, `chore/`

Example: `feat/42-add-k6-extension`

## Commit Style

Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`

## AI Disclosure

If you used AI assistance beyond minor autocomplete, disclose it in your PR.
All contributions must demonstrate human understanding and real-world testing.

## Code of Conduct

Be respectful. This project follows the [Contributor Covenant](https://www.contributor-covenant.org/).
