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

    supports_skills: bool = False
    default_mode: str = "commands"  # "commands" | "skills"
    multi_install_safe: bool = False  # True if the integration has a fully isolated command dir

    @classmethod
    def get_commands_dir(cls, project_root: Path) -> Path:
        folder = cls.config.get("folder", "")
        return project_root / str(folder)

    @classmethod
    def get_context_file(cls, project_root: Path) -> Path | None:
        if cls.context_file:
            return project_root / cls.context_file
        return None

    @classmethod
    def get_skills_dir(cls, project_root: Path) -> Path:
        skills_folder = cls.registrar_config.get("skills_dir", ".agents/skills")
        return project_root / str(skills_folder)

    @classmethod
    @abstractmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        """Render a command template into the agent-specific format."""

    @classmethod
    def render_skill(cls, name: str, content: str, description: str = "") -> str:
        """Render a skill file. Default: raw markdown content."""
        return content

    @classmethod
    def command_extension(cls) -> str:
        return str(cls.registrar_config.get("extension", ".md"))

    @classmethod
    def args_placeholder(cls) -> str:
        return str(cls.registrar_config.get("args_placeholder", "$ARGUMENTS"))


class MarkdownIntegration(IntegrationBase):
    """Integration that stores commands as .md files."""

    @classmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        return content

    @classmethod
    def command_extension(cls) -> str:
        return str(cls.registrar_config.get("extension", ".md"))

    @classmethod
    def args_placeholder(cls) -> str:
        return str(cls.registrar_config.get("args_placeholder", "$ARGUMENTS"))


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
        return str(cls.registrar_config.get("extension", ".toml"))

    @classmethod
    def args_placeholder(cls) -> str:
        return str(cls.registrar_config.get("args_placeholder", "{{args}}"))


class YamlIntegration(IntegrationBase):
    """Integration that stores commands as Goose YAML recipe files.

    Goose (Block) reads .yaml recipe files from .goose/recipes/.
    Each file has a header (version, title, description, parameters,
    extensions, activities) followed by a `prompt: |` block scalar.
    Argument placeholder: {{args}}
    """

    @classmethod
    def render_command(cls, name: str, content: str, description: str = "") -> str:
        """Render a command as a Goose YAML recipe."""
        import yaml as _yaml

        title = name
        if title.startswith("qakit."):
            title = title[len("qakit.") :]
        title = title.replace(".", " ").replace("-", " ").replace("_", " ").title()

        header: dict[str, Any] = {
            "version": "1.0.0",
            "title": title,
            "description": description or title,
            "author": {"contact": "qa-kit"},
            "parameters": [
                {
                    "key": "args",
                    "input_type": "string",
                    "requirement": "optional",
                    "default": "",
                    "description": "User input passed to the command.",
                }
            ],
            "extensions": [{"type": "builtin", "name": "developer"}],
            "activities": ["QA Automation"],
        }

        header_yaml = _yaml.safe_dump(
            header,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ).strip()

        indented = "\n".join(f"  {line}" for line in content.split("\n"))
        return f"{header_yaml}\nprompt: |\n{indented}\n"

    @classmethod
    def command_extension(cls) -> str:
        return str(cls.registrar_config.get("extension", ".yaml"))

    @classmethod
    def args_placeholder(cls) -> str:
        return str(cls.registrar_config.get("args_placeholder", "{{args}}"))
