"""Codex CLI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class CodexIntegration(MarkdownIntegration):
    key = "codex"
    config = {
        "name": "Codex CLI",
        "folder": ".codex/commands/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".codex/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
