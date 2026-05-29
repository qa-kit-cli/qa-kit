"""Roo Code integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class RooIntegration(MarkdownIntegration):
    key = "roo"
    config = {
        "name": "Roo Code",
        "folder": ".roo/commands/",
        "install_url": "https://roocode.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".roo/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
