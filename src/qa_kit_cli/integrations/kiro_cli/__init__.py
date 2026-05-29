"""Kiro CLI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class KiroIntegration(MarkdownIntegration):
    key = "kiro"
    config = {
        "name": "Kiro CLI",
        "folder": ".kiro/commands/",
        "install_url": "https://kiro.dev",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".kiro/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
