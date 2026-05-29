"""Tests that generated templates and QA artifacts contain no speckit/specify references."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from qa_kit_cli._assets import get_commands_dir, get_templates_dir


# Patterns that MUST NOT appear in qa-kit artifacts
_FORBIDDEN = [
    r"\bspeckit\b",
    r"\bspec-kit\b",
    r"\.specify/",
    r"\bspecs/<feature>",
]


def _check_file(path: Path) -> list[str]:
    """Return list of forbidden pattern matches found in path."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return []
    findings: list[str] = []
    for pat in _FORBIDDEN:
        matches = re.findall(pat, content, flags=re.IGNORECASE)
        if matches:
            findings.append(f"{path}: found '{pat}' → {matches[:3]}")
    return findings


def _all_template_files() -> list[Path]:
    files: list[Path] = []
    for d in [get_commands_dir(), get_templates_dir()]:
        if d.exists():
            files.extend(p for p in d.rglob("*") if p.is_file())
    return files


# ---------------------------------------------------------------------------
# Command templates
# ---------------------------------------------------------------------------

def test_command_templates_have_no_speckit_references() -> None:
    commands_dir = get_commands_dir()
    assert commands_dir.exists(), f"Commands dir not found: {commands_dir}"
    violations: list[str] = []
    for f in commands_dir.rglob("*.md"):
        violations.extend(_check_file(f))
    assert not violations, "Forbidden references found in command templates:\n" + "\n".join(violations)


def test_memory_templates_have_no_speckit_references() -> None:
    templates_dir = get_templates_dir()
    assert templates_dir.exists()
    violations: list[str] = []
    for f in templates_dir.rglob("*.md"):
        violations.extend(_check_file(f))
    assert not violations, "Forbidden references in memory templates:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# qakit memory artifacts (all defined in _MEMORY_TEMPLATES) reference .qakit/
# ---------------------------------------------------------------------------

def test_memory_template_names_use_qakit_path() -> None:
    from qa_kit_cli.shared_infra import _MEMORY_TEMPLATES

    for _src, target in _MEMORY_TEMPLATES.items():
        # target should be a plain filename, not a .specify/ path
        assert ".specify" not in target, f"Memory target '{target}' references .specify/"
        assert "specs/" not in target, f"Memory target '{target}' references specs/"


# ---------------------------------------------------------------------------
# Command manifest command IDs use qakit. prefix
# ---------------------------------------------------------------------------

def test_command_ids_use_qakit_prefix() -> None:
    from qa_kit_cli.agents import COMMAND_MANIFEST

    for spec in COMMAND_MANIFEST:
        assert spec.command_id.startswith("qakit."), (
            f"Command '{spec.command_id}' does not use 'qakit.' prefix"
        )
        assert "speckit" not in spec.command_id.lower(), (
            f"Command '{spec.command_id}' contains 'speckit'"
        )


# ---------------------------------------------------------------------------
# Skill names from SkillRegistrar use qakit- prefix
# ---------------------------------------------------------------------------

def test_skill_slugs_use_qakit_prefix() -> None:
    from qa_kit_cli.agents import COMMAND_MANIFEST

    for spec in COMMAND_MANIFEST:
        slug = spec.command_id.replace(".", "-")
        assert slug.startswith("qakit-"), f"Skill slug '{slug}' does not start with 'qakit-'"
        assert "speckit" not in slug.lower(), f"Skill slug '{slug}' contains 'speckit'"


# ---------------------------------------------------------------------------
# All memory artifacts live under .qakit/memory/
# ---------------------------------------------------------------------------

def test_all_memory_files_created_on_init(project_dir: Path) -> None:
    from qa_kit_cli.shared_infra import _MEMORY_TEMPLATES, ensure_memory_files

    ensure_memory_files(project_dir)
    memory_dir = project_dir / ".qakit" / "memory"
    for _src, target_name in _MEMORY_TEMPLATES.items():
        target = memory_dir / target_name
        assert target.exists(), f"Memory file '{target_name}' was not created on init"
