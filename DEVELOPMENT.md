# Development Guide

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pipx
- Node.js 18+ (to test generated CI configs and Playwright commands)

## Setup

```bash
git clone https://github.com/qa-kit-cli/qa-kit.git
cd qa-kit
uv sync --extra dev --extra test
```

## Project Layout

```
src/qa_kit_cli/          Python CLI package
templates/commands/      Slash command .md templates
templates/               Core document templates
presets/                 Bundled preset definitions
extensions/              Extension docs + bundled extension definitions
integrations/            Integration catalog + per-agent Python classes
scripts/                 Bash + PowerShell helper scripts
tests/                   pytest test suite
```

## Running the CLI in Development

```bash
# Run directly from source (no install needed)
uv run qakit --help
uv run qakit init
uv run qakit version
```

## Adding a New Slash Command

1. Create `templates/commands/<category>.<name>.md`
2. Follow the template format: YAML frontmatter + `## PROTOCOL` sections
3. Register it in `src/qa_kit_cli/agents.py` in the `COMMAND_MANIFEST` list
4. Add a lifecycle hook event in `src/qa_kit_cli/extensions.py` if needed
5. Test in at least one AI agent

## Adding a New AI Agent Integration

1. Create `src/qa_kit_cli/integrations/<agent_key>/__init__.py`
2. Implement class extending `MarkdownIntegration` (or `TomlIntegration` for TOML-format agents)
3. Register in `src/qa_kit_cli/integrations/__init__.py` via `_register_builtins()`
4. Add catalog entry in `integrations/catalog.json`
5. Write tests in `tests/test_agents.py`

## Adding a New Preset

See `presets/PUBLISHING.md` for the full guide.

## Adding a New Extension

See `extensions/EXTENSION-DEVELOPMENT-GUIDE.md` for the full guide.

## Asset Bundling

All files under `templates/`, `scripts/`, `presets/`, and the bundled `extensions/` subdirs are
included in the wheel via `pyproject.toml` `force-include` declarations. They land in
`qa_kit_cli/core_pack/` inside the installed package.

The `_assets.py` module resolves `core_pack/` whether running from source or from an installed wheel.

## Release Process

1. Update version in `pyproject.toml` and `src/qa_kit_cli/_version.py`
2. Update `CHANGELOG.md`
3. Create a git tag `vX.Y.Z`
4. The `release.yml` GitHub Actions workflow publishes to PyPI automatically
