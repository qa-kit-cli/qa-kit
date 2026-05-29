"""Pi Coding Agent integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class PiIntegration(MarkdownIntegration):
    key = "pi"
    config = {
        "name": "Pi Coding Agent",
        "folder": ".pi/commands/",
        "install_url": "https://pi.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".pi/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
