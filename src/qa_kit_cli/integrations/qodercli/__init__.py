"""Qoder CLI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class QoderIntegration(MarkdownIntegration):
    key = "qodercli"
    config = {
        "name": "Qoder CLI",
        "folder": ".qoder/commands/",
        "install_url": "https://qoder.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".qoder/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
