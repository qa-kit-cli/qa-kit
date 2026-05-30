"""Tests that CommandRegistrar rejects path traversal attacks."""
from __future__ import annotations

from pathlib import Path

import pytest

from qa_kit_cli.agents import CommandRegistrar


def test_ensure_inside_accepts_valid_path(tmp_path: Path) -> None:
    base = tmp_path / "commands"
    target = base / "qakit.strategy.md"
    CommandRegistrar._ensure_inside(target, base)


def test_ensure_inside_accepts_nested_valid_path(tmp_path: Path) -> None:
    base = tmp_path / "commands"
    target = base / "sub" / "qakit.strategy.md"
    CommandRegistrar._ensure_inside(target, base)


def test_ensure_inside_rejects_parent_traversal(tmp_path: Path) -> None:
    base = tmp_path / "commands"
    evil = base / ".." / ".bashrc"
    with pytest.raises(ValueError, match="escapes"):
        CommandRegistrar._ensure_inside(evil, base)


def test_ensure_inside_rejects_absolute_escape(tmp_path: Path) -> None:
    base = tmp_path / "commands"
    evil = Path("/etc/passwd")
    with pytest.raises(ValueError, match="escapes"):
        CommandRegistrar._ensure_inside(evil, base)


def test_ensure_inside_rejects_double_traversal(tmp_path: Path) -> None:
    base = tmp_path / "commands"
    evil = base / "sub" / ".." / ".." / "secret.txt"
    with pytest.raises(ValueError, match="escapes"):
        CommandRegistrar._ensure_inside(evil, base)
