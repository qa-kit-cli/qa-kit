"""Forge integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class ForgeIntegration(MarkdownIntegration):
    key = "forge"
    config = {
        "name": "Forge",
        "folder": ".forge/commands/",
        "install_url": "https://forge.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".forge/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
