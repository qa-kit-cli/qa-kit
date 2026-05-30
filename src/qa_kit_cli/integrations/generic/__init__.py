"""Generic/BYOA (bring your own agent) integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class GenericIntegration(MarkdownIntegration):
    key = "generic"
    config = {
        "name": "Generic (BYOA)",
        "folder": ".generic/commands/",
        "install_url": None,
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".generic/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
