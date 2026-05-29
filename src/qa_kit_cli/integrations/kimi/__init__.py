"""Kimi Code integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class KimiIntegration(MarkdownIntegration):
    key = "kimi"
    config = {
        "name": "Kimi Code",
        "folder": ".kimi/commands/",
        "install_url": "https://kimi.moonshot.cn",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".kimi/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
