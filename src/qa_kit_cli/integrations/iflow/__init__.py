"""iFlow CLI integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class IFlowIntegration(MarkdownIntegration):
    key = "iflow"
    config = {
        "name": "iFlow CLI",
        "folder": ".iflow/commands/",
        "install_url": "https://iflow.ai",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".iflow/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
