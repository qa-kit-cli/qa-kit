"""Tests for the SHA-256 file manifest used to track installed command files."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli._utils import sha256_file
from qa_kit_cli.integrations.manifest import (
    get_recorded_files,
    record_files,
    uninstall_files,
)


def _make_qakit(tmp_path: Path) -> Path:
    qakit_dir = tmp_path / ".qakit"
    qakit_dir.mkdir()
    return qakit_dir


def test_record_files_creates_manifest(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "strategy.md"
    f.write_text("hello", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    manifest = get_recorded_files(qakit_dir, "claude")
    assert str(f) in manifest


def test_record_files_stores_correct_sha256(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "write.playwright.md"
    f.write_text("world", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    manifest = get_recorded_files(qakit_dir, "claude")
    assert manifest[str(f)] == sha256_file(f)


def test_uninstall_files_removes_unchanged_file(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "cmd.md"
    f.write_text("original content", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    removed, skipped = uninstall_files(qakit_dir, "claude")
    assert f in removed
    assert not skipped
    assert not f.exists()


def test_uninstall_files_skips_modified_file(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "cmd.md"
    f.write_text("original content", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    f.write_text("user modified this file", encoding="utf-8")

    removed, skipped = uninstall_files(qakit_dir, "claude")
    assert f not in removed
    assert f in skipped
    assert f.exists()


def test_uninstall_files_force_removes_modified_file(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "cmd.md"
    f.write_text("original content", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    f.write_text("user modified this file", encoding="utf-8")

    removed, skipped = uninstall_files(qakit_dir, "claude", force=True)
    assert f in removed
    assert not skipped
    assert not f.exists()


def test_uninstall_files_deletes_manifest_file(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "x.md"
    f.write_text("content", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    manifest_path = qakit_dir / "integrations" / "claude.manifest.json"
    assert manifest_path.exists()

    uninstall_files(qakit_dir, "claude")
    assert not manifest_path.exists()


def test_get_recorded_files_returns_empty_dict_when_no_manifest(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    result = get_recorded_files(qakit_dir, "nonexistent-integration")
    assert result == {}


def test_uninstall_files_does_not_raise_when_file_already_deleted(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "gone.md"
    f.write_text("data", encoding="utf-8")

    record_files(qakit_dir, "claude", [f])
    f.unlink()

    removed, skipped = uninstall_files(qakit_dir, "claude")
    assert f not in removed


def test_record_files_overwrites_previous_manifest(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")

    record_files(qakit_dir, "claude", [a])
    record_files(qakit_dir, "claude", [b])

    manifest = get_recorded_files(qakit_dir, "claude")
    assert str(a) not in manifest
    assert str(b) in manifest


def test_record_files_multiple_integrations_are_independent(tmp_path: Path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f1 = tmp_path / "claude.md"
    f2 = tmp_path / "copilot.md"
    f1.write_text("claude content", encoding="utf-8")
    f2.write_text("copilot content", encoding="utf-8")

    record_files(qakit_dir, "claude", [f1])
    record_files(qakit_dir, "copilot", [f2])

    claude_manifest = get_recorded_files(qakit_dir, "claude")
    copilot_manifest = get_recorded_files(qakit_dir, "copilot")

    assert str(f1) in claude_manifest
    assert str(f2) not in claude_manifest
    assert str(f2) in copilot_manifest
    assert str(f1) not in copilot_manifest
