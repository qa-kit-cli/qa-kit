"""Codex CLI integration."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations.base import MarkdownIntegration


class CodexIntegration(MarkdownIntegration):
    key = "codex"
    config = {
        "name": "Codex CLI",
        "folder": ".codex/commands/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".codex/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
        "skills_dir": ".agents/skills",
    }
    supports_skills = True
    default_mode = "commands"

    @classmethod
    def get_skills_dir(cls, project_root: Path) -> Path:
        return project_root / ".agents" / "skills"
