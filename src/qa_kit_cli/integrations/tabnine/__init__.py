"""Tabnine integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class TabnineIntegration(MarkdownIntegration):
    key = "tabnine"
    config = {
        "name": "Tabnine",
        "folder": ".tabnine/commands/",
        "install_url": "https://www.tabnine.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".tabnine/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
