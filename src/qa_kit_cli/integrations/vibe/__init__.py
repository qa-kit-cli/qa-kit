"""Mistral Vibe integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class VibeIntegration(MarkdownIntegration):
    key = "vibe"
    config = {
        "name": "Mistral Vibe",
        "folder": ".vibe/commands/",
        "install_url": "https://mistral.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".vibe/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
