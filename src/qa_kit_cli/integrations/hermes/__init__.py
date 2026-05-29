"""Hermes Agent integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class HermesIntegration(MarkdownIntegration):
    key = "hermes"
    config = {
        "name": "Hermes Agent",
        "folder": ".hermes/commands/",
        "install_url": "https://hermes.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".hermes/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
