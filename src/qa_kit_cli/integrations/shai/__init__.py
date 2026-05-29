"""SHAI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class ShaiIntegration(MarkdownIntegration):
    key = "shai"
    config = {
        "name": "SHAI",
        "folder": ".shai/commands/",
        "install_url": "https://shai.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".shai/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
