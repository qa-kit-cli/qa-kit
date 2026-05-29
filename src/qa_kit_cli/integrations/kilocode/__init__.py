"""Kilo Code integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class KiloCodeIntegration(MarkdownIntegration):
    key = "kilocode"
    config = {
        "name": "Kilo Code",
        "folder": ".kilocode/commands/",
        "install_url": "https://kilocode.ai",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".kilocode/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
