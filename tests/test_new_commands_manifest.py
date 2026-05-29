"""Tests for the 7 new QA lifecycle commands added in Phase 8."""

from __future__ import annotations

from pathlib import Path

import pytest

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli.agents import COMMAND_MANIFEST, CommandRegistrar
from qa_kit_cli.shared_infra import ensure_project_layout

NEW_COMMANDS = [
    "qakit.tasks",
    "qakit.checklist",
    "qakit.traceability",
    "qakit.regression",
    "qakit.defects",
    "qakit.release-gate",
    "qakit.env",
]

NEW_TEMPLATES = [
    "tasks.md",
    "checklist.md",
    "traceability.md",
    "regression.md",
    "defects.md",
    "release-gate.md",
    "env.md",
]


def test_new_commands_present_in_manifest() -> None:
    ids = [spec.command_id for spec in COMMAND_MANIFEST]
    for cmd in NEW_COMMANDS:
        assert cmd in ids, f"Command '{cmd}' missing from COMMAND_MANIFEST"


def test_new_templates_exist_on_disk() -> None:
    commands_dir = get_commands_dir()
    missing = [t for t in NEW_TEMPLATES if not (commands_dir / t).exists()]
    assert not missing, f"Missing template files: {missing}"


def test_new_templates_have_frontmatter() -> None:
    commands_dir = get_commands_dir()
    bad = []
    for t in NEW_TEMPLATES:
        content = (commands_dir / t).read_text(encoding="utf-8")
        if not content.startswith("---"):
            bad.append(t)
    assert not bad, f"Templates missing YAML frontmatter: {bad}"


def test_new_templates_have_command_field() -> None:
    commands_dir = get_commands_dir()
    bad = []
    for t in NEW_TEMPLATES:
        parts = (commands_dir / t).read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3 or "command:" not in parts[1]:
            bad.append(t)
    assert not bad, f"Templates missing 'command:' in frontmatter: {bad}"


def test_new_commands_install_for_claude(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    CommandRegistrar().install_for_integration(project_dir, qakit_dir, "claude")
    for cmd in NEW_COMMANDS:
        path = project_dir / ".claude" / "commands" / f"{cmd}.md"
        assert path.exists(), f"Installed file missing: {path}"


def test_new_memory_templates_created_on_init(project_dir) -> None:
    from qa_kit_cli.shared_infra import ensure_memory_files

    ensure_memory_files(project_dir)
    memory_dir = project_dir / ".qakit" / "memory"
    expected = [
        "test-tasks.md",
        "qa-checklist.md",
        "traceability-matrix.md",
        "regression-suite.md",
        "defect-summary.md",
        "release-gate.md",
        "test-environments.md",
    ]
    missing = [f for f in expected if not (memory_dir / f).exists()]
    assert not missing, f"Memory files not created: {missing}"
