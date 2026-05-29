"""CodeBuddy integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class CodeBuddyIntegration(MarkdownIntegration):
    key = "codebuddy"
    config = {
        "name": "CodeBuddy",
        "folder": ".codebuddy/commands/",
        "install_url": "https://codebuddy.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".codebuddy/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
