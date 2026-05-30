"""Tabnine integration (TOML format)."""

from qa_kit_cli.integrations.base import TomlIntegration


class TabnineIntegration(TomlIntegration):
    key = "tabnine"
    config = {
        "name": "Tabnine",
        "folder": ".tabnine/commands/",
        "install_url": "https://www.tabnine.com",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".tabnine/commands/",
        "format": "toml",
        "args_placeholder": "{{args}}",
        "extension": ".toml",
    }
