"""Trae integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class TraeIntegration(MarkdownIntegration):
    key = "trae"
    config = {
        "name": "Trae",
        "folder": ".trae/commands/",
        "install_url": "https://trae.ai",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".trae/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
