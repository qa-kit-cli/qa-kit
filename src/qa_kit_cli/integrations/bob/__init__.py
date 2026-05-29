"""IBM Bob integration."""

from qa_kit_cli.integrations.base import MarkdownIntegration


class BobIntegration(MarkdownIntegration):
    key = "bob"
    config = {
        "name": "IBM Bob",
        "folder": ".bob/commands/",
        "install_url": "https://ibm.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".bob/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
    }
