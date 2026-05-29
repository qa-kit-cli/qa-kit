"""Tests for modified file preservation on integration uninstall/upgrade."""

from __future__ import annotations

from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.integrations.manifest import get_modified_files, record_files, uninstall_files
from qa_kit_cli.shared_infra import ensure_project_layout


def _make_qakit(tmp_path):
    qakit_dir = ensure_project_layout(tmp_path)
    (qakit_dir / "integrations").mkdir(exist_ok=True)
    return qakit_dir


def test_get_modified_files_empty_when_unchanged(tmp_path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "a.md"
    f.write_text("original", encoding="utf-8")
    record_files(qakit_dir, "test", [f])
    assert get_modified_files(qakit_dir, "test") == []


def test_get_modified_files_detects_local_change(tmp_path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "a.md"
    f.write_text("original", encoding="utf-8")
    record_files(qakit_dir, "test", [f])
    f.write_text("modified by user", encoding="utf-8")
    modified = get_modified_files(qakit_dir, "test")
    assert f in modified


def test_uninstall_preserves_modified_by_default(tmp_path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "cmd.md"
    f.write_text("original", encoding="utf-8")
    record_files(qakit_dir, "test", [f])
    f.write_text("user edit", encoding="utf-8")

    removed, skipped = uninstall_files(qakit_dir, "test", force=False)
    assert f in skipped
    assert f not in removed
    assert f.exists()


def test_uninstall_force_removes_modified(tmp_path) -> None:
    qakit_dir = _make_qakit(tmp_path)
    f = tmp_path / "cmd.md"
    f.write_text("original", encoding="utf-8")
    record_files(qakit_dir, "test", [f])
    f.write_text("user edit", encoding="utf-8")

    removed, skipped = uninstall_files(qakit_dir, "test", force=True)
    assert f in removed
    assert not skipped
    assert not f.exists()


def test_integration_remove_via_cli_preserves_modified(project_dir) -> None:
    runner = CliRunner()
    # Install
    runner.invoke(app, ["init", "--integration", "claude"])

    # Modify a managed file
    cmd_file = project_dir / ".claude" / "commands" / "qakit.strategy.md"
    assert cmd_file.exists()
    cmd_file.write_text("user customized content", encoding="utf-8")

    # Remove without --force
    result = runner.invoke(app, ["integration", "remove", "claude"])
    assert result.exit_code == 0
    # Modified file should still exist
    assert cmd_file.exists()


def test_integration_remove_force_removes_modified(project_dir) -> None:
    runner = CliRunner()
    runner.invoke(app, ["init", "--integration", "claude"])

    cmd_file = project_dir / ".claude" / "commands" / "qakit.strategy.md"
    cmd_file.write_text("user customized content", encoding="utf-8")

    result = runner.invoke(app, ["integration", "remove", "claude", "--force"])
    assert result.exit_code == 0
    assert not cmd_file.exists()
