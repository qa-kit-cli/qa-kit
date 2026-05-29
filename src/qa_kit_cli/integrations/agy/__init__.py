"""Antigravity (agy) integration."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations.base import MarkdownIntegration


class AgyIntegration(MarkdownIntegration):
    key = "agy"
    config = {
        "name": "Antigravity",
        "folder": ".agy/commands/",
        "install_url": "https://github.com/antigravity-ai/agy",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".agy/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
        "skills_dir": ".agy/skills/",
    }
    supports_skills = True
    default_mode = "skills"
    multi_install_safe = True

    @classmethod
    def get_skills_dir(cls, project_root: Path) -> Path:
        return project_root / ".agy" / "skills"
