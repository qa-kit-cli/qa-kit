"""Qwen Code integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class QwenIntegration(MarkdownIntegration):
    key = "qwen"
    config = {
        "name": "Qwen Code",
        "folder": ".qwen/commands/",
        "install_url": "https://qwenlm.github.io",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".qwen/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
