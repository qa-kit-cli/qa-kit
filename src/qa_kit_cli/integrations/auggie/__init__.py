"""Auggie CLI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class AuggieIntegration(MarkdownIntegration):
    key = "auggie"
    config = {
        "name": "Auggie CLI",
        "folder": ".auggie/commands/",
        "install_url": "https://auggie.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".auggie/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
