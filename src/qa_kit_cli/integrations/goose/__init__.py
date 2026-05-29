"""Goose integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class GooseIntegration(MarkdownIntegration):
    key = "goose"
    config = {
        "name": "Goose",
        "folder": ".goose/commands/",
        "install_url": "https://block.github.io/goose",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".goose/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
