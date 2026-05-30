"""Goose integration — Block's open-source AI agent.

Goose reads YAML recipe files from .goose/recipes/.
Each file uses the Goose recipe schema: version, title, description,
parameters, extensions, activities, and a `prompt: |` block scalar.
Argument placeholder: {{args}}
"""

from qa_kit_cli.integrations.base import YamlIntegration


class GooseIntegration(YamlIntegration):
    key = "goose"
    config = {
        "name": "Goose",
        "folder": ".goose/",
        "install_url": "https://block.github.io/goose/docs/getting-started/installation",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".goose/recipes",
        "format": "yaml",
        "args_placeholder": "{{args}}",
        "extension": ".yaml",
    }
    context_file = "AGENTS.md"
