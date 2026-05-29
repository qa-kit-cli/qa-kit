"""Amp integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class AmpIntegration(MarkdownIntegration):
    key = "amp"
    config = {
        "name": "Amp",
        "folder": ".amp/commands/",
        "install_url": "https://ampcode.com",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".amp/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
