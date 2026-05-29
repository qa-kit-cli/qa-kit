"""Gemini CLI integration (TOML format)."""

from qa_kit_cli.integrations.base import TomlIntegration


class GeminiIntegration(TomlIntegration):
    key = "gemini"
    config = {
        "name": "Gemini CLI",
        "folder": ".gemini/commands/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".gemini/commands/",
        "format": "toml",
        "args_placeholder": "{{args}}",
        "extension": ".toml",
    }
    context_file = ".gemini/GEMINI.md"
