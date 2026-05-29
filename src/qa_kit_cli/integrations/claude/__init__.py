"""Claude Code integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class ClaudeIntegration(MarkdownIntegration):
    key = "claude"
    config = {
        "name": "Claude Code",
        "folder": ".claude/commands/",
        "install_url": "https://claude.ai/download",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".claude/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".claude/CLAUDE.md"
