"""Cursor integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class CursorIntegration(MarkdownIntegration):
    key = "cursor"
    config = {
        "name": "Cursor",
        "folder": ".cursor/rules/",
        "install_url": "https://cursor.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".cursor/rules/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".mdc",
    }
    context_file = ".cursorrules"


class CursorAgentIntegration(CursorIntegration):
    """
    Backward-compatible alias for users that refer to this integration as
    "cursor-agent" (matches spec naming).
    """

    key = "cursor-agent"
