"""Lingma integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class LingmaIntegration(MarkdownIntegration):
    key = "lingma"
    config = {
        "name": "Lingma",
        "folder": ".lingma/commands/",
        "install_url": "https://lingma.aliyun.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".lingma/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
