"""Validate that all slash command templates are well-formed."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli.agents import COMMAND_MANIFEST


def _template_files() -> list[Path]:
    commands_dir = get_commands_dir()
    return [commands_dir / spec.template_name for spec in COMMAND_MANIFEST]


# ---------------------------------------------------------------------------
# COMMAND_MANIFEST integrity
# ---------------------------------------------------------------------------


def test_command_manifest_count_is_36() -> None:
    assert len(COMMAND_MANIFEST) == 36


def test_command_manifest_command_ids_are_unique() -> None:
    ids = [spec.command_id for spec in COMMAND_MANIFEST]
    assert len(ids) == len(set(ids))


def test_command_manifest_template_names_are_unique() -> None:
    names = [spec.template_name for spec in COMMAND_MANIFEST]
    assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_all_command_templates_exist_on_disk() -> None:
    missing = [f for f in _template_files() if not f.exists()]
    assert not missing, f"Missing template files: {[f.name for f in missing]}"


def test_command_templates_are_non_empty() -> None:
    short = [f for f in _template_files() if len(f.read_text(encoding="utf-8").strip()) < 100]
    assert not short, f"Suspiciously short template files: {[f.name for f in short]}"


# ---------------------------------------------------------------------------
# YAML frontmatter validation
# ---------------------------------------------------------------------------


def test_all_templates_start_with_yaml_frontmatter() -> None:
    bad = [f for f in _template_files() if not f.read_text(encoding="utf-8").startswith("---")]
    assert not bad, f"Templates missing YAML frontmatter: {[f.name for f in bad]}"


def test_all_templates_have_command_field_in_frontmatter() -> None:
    bad = []
    for path in _template_files():
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3 or "command:" not in parts[1]:
            bad.append(path.name)
    assert not bad, f"Templates missing 'command:' in frontmatter: {bad}"


def test_all_templates_have_description_field_in_frontmatter() -> None:
    bad = []
    for path in _template_files():
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3 or "description:" not in parts[1]:
            bad.append(path.name)
    assert not bad, f"Templates missing 'description:' in frontmatter: {bad}"


# ---------------------------------------------------------------------------
# Frontmatter command ID matches COMMAND_MANIFEST
# ---------------------------------------------------------------------------


def test_template_command_ids_match_command_manifest() -> None:
    commands_dir = get_commands_dir()
    mismatches = []
    for spec in COMMAND_MANIFEST:
        path = commands_dir / spec.template_name
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            mismatches.append(f"{spec.template_name}: malformed frontmatter")
            continue
        match = re.search(r"^command:\s*(.+)$", parts[1], re.MULTILINE)
        if not match:
            mismatches.append(f"{spec.template_name}: no 'command:' in frontmatter")
            continue
        found = match.group(1).strip()
        if found != spec.command_id:
            mismatches.append(
                f"{spec.template_name}: command={found!r} but spec says {spec.command_id!r}"
            )
    assert not mismatches, "\n".join(mismatches)


# ---------------------------------------------------------------------------
# Category coverage
# ---------------------------------------------------------------------------


def test_strategy_commands_present() -> None:
    ids = {s.command_id for s in COMMAND_MANIFEST}
    for cmd in ["qakit.strategy", "qakit.testplan", "qakit.coverage", "qakit.gaps",
                "qakit.policy", "qakit.clarify", "qakit.pyramid"]:
        assert cmd in ids, f"Missing strategy command: {cmd}"


def test_write_commands_present() -> None:
    ids = {s.command_id for s in COMMAND_MANIFEST}
    for cmd in ["qakit.write.playwright", "qakit.write.cypress", "qakit.write.jest",
                "qakit.write.vitest", "qakit.write.selenium", "qakit.write.a11y",
                "qakit.write.api", "qakit.write.visual", "qakit.write.pom",
                "qakit.write.fixtures"]:
        assert cmd in ids, f"Missing write command: {cmd}"


def test_ci_commands_present() -> None:
    ids = {s.command_id for s in COMMAND_MANIFEST}
    for cmd in ["qakit.ci.github-actions", "qakit.ci.jenkins", "qakit.ci.matrix",
                "qakit.ci.badges", "qakit.ci.report"]:
        assert cmd in ids, f"Missing CI command: {cmd}"


def test_maintain_commands_present() -> None:
    ids = {s.command_id for s in COMMAND_MANIFEST}
    for cmd in ["qakit.maintain.flaky", "qakit.maintain.refactor",
                "qakit.maintain.data", "qakit.maintain.upgrade"]:
        assert cmd in ids, f"Missing maintain command: {cmd}"


def test_review_commands_present() -> None:
    ids = {s.command_id for s in COMMAND_MANIFEST}
    for cmd in ["qakit.review.pr", "qakit.review.bugreport", "qakit.review.accessibility"]:
        assert cmd in ids, f"Missing review command: {cmd}"
