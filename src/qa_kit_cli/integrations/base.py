"""Base classes for AI agent integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class IntegrationBase(ABC):
    """Abstract base for all AI agent integrations."""

    key: str = ""
    config: dict[str, Any] = {}
    registrar_config: dict[str, Any] = {}
    context_file: str | None = None

    @classmethod
    def get_commands_dir(cls, project_root: Path) -> Path:
        folder = cls.config.get("folder", "")
        return project_root / folder

    @classmethod
    def get_context_file(cls, project_root: Path) -> Path | None:
        if cls.context_file:
            return project_root / cls.context_file
        return None

    @classmethod
    @abstractmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        """Render a command template into the agent-specific format."""


class MarkdownIntegration(IntegrationBase):
    """Integration that stores commands as .md files."""

    @classmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        return content

    @classmethod
    def command_extension(cls) -> str:
        return cls.registrar_config.get("extension", ".md")

    @classmethod
    def args_placeholder(cls) -> str:
        return cls.registrar_config.get("args_placeholder", "$ARGUMENTS")


class TomlIntegration(IntegrationBase):
    """Integration that stores commands as .toml files (e.g. Gemini CLI)."""

    @classmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        safe_desc = description.replace('"', '\\"')
        safe_content = content.replace('"""', "'''")
        return f'''[[commands]]
name = "{name}"
description = "{safe_desc}"
prompt = """
{safe_content}
"""
'''

    @classmethod
    def command_extension(cls) -> str:
        return cls.registrar_config.get("extension", ".toml")

    @classmethod
    def args_placeholder(cls) -> str:
        return cls.registrar_config.get("args_placeholder", "{{args}}")
