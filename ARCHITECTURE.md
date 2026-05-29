# QA Kit Architecture

QA Kit follows the same CLI architecture patterns established by spec-kit (github/spec-kit, MIT license), adapted for QA automation workflows. We credit spec-kit as the inspiration for the integration/preset/extension system design.

## System Layout

- `src/qa_kit_cli/`: CLI app, command groups, integration registry, preset/extension managers, workflow engine.
- `templates/commands/`: slash-command templates rendered into agent-specific command or skills directories.
- `presets/`: framework-specific composition overrides layered into command rendering.
- `extensions/`: lifecycle hook and command extensions for external QA tooling.
- `workflows/`: bundled YAML workflows executed by the workflow engine.
- `.qakit/`: project-local runtime state (memory, integrations, presets, extensions, workflows, config).

## Resolution Model

QA Kit uses layered resolution for command templates:

1. Project overrides (`.qakit/templates/overrides`)
2. Enabled presets (priority ordered)
3. Enabled extensions (priority ordered)
4. Bundled core templates

## Integration Model

- Integrations define agent-specific command/skills locations and rendering behavior.
- Integration state is persisted in `.qakit/integration.json`.
- Multi-install safety flags prevent unsafe side-by-side installs by default.

## Catalog Model

Catalog resolution supports four source levels:

1. Environment variable overrides
2. Project config (`.qakit/catalogs.yml`)
3. User config (`<user_config_dir>/catalogs.yml`)
4. Bundled catalogs

## Acknowledgements

QA Kit's CLI architecture, extension/preset system, and multi-agent integration model are inspired by spec-kit (https://github.com/github/spec-kit) by GitHub, Inc., licensed under MIT. QA Kit is an independent project and is not affiliated with or endorsed by GitHub.
