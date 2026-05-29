"""Devin integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class DevinIntegration(MarkdownIntegration):
    key = "devin"
    config = {
        "name": "Devin",
        "folder": ".devin/commands/",
        "install_url": "https://devin.ai",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".devin/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
