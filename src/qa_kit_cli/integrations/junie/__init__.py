"""Junie integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class JunieIntegration(MarkdownIntegration):
    key = "junie"
    config = {
        "name": "Junie",
        "folder": ".junie/commands/",
        "install_url": "https://www.jetbrains.com/junie/",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".junie/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
