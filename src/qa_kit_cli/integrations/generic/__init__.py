"""Generic / bring-your-own-agent integration fallback."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class GenericIntegration(MarkdownIntegration):
    key = "generic"
    config = {
        "name": "Generic Agent",
        "folder": ".ai/commands/",
        "install_url": "",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".ai/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
