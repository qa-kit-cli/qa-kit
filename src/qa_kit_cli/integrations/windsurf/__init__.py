"""Windsurf integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class WindsurfIntegration(MarkdownIntegration):
    key = "windsurf"
    config = {
        "name": "Windsurf",
        "folder": ".windsurf/rules/",
        "install_url": "https://windsurf.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".windsurf/rules/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".windsurfrules"
