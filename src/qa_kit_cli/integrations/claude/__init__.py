"""Claude Code integration."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations.base import MarkdownIntegration


class ClaudeIntegration(MarkdownIntegration):
    key = "claude"
    config = {
        "name": "Claude Code",
        "folder": ".claude/commands/",
        "install_url": "https://claude.ai/download",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".claude/commands/",
        "format": "markdown",
        "args_placeholder": "$ARGUMENTS",
        "extension": ".md",
        "skills_dir": ".claude/skills",
    }
    context_file = ".claude/CLAUDE.md"
    supports_skills = True
    default_mode = "commands"
    multi_install_safe = True

    @classmethod
    def get_skills_dir(cls, project_root: Path) -> Path:
        return project_root / ".claude" / "skills"

    @classmethod
    def render_skill(cls, name: str, content: str, description: str = "") -> str:
        safe_desc = description or name
        return f"---\ndescription: {safe_desc}\n---\n\n{content}\n"
