"""GitHub Copilot integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class CopilotIntegration(MarkdownIntegration):
    key = "copilot"
    config = {
        "name": "GitHub Copilot",
        "folder": ".github/copilot-instructions/",
        "install_url": "https://github.com/features/copilot",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".github/copilot-instructions/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".github/copilot-instructions.md"
