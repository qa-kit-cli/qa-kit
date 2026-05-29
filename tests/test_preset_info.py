from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.shared_infra import ensure_project_layout


def test_preset_info_installed(project_dir: Path) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    add_result = runner.invoke(app, ["preset", "add", "playwright"])
    assert add_result.exit_code == 0, add_result.output

    result = runner.invoke(app, ["preset", "info", "playwright"])
    assert result.exit_code == 0, result.output
    assert "Installed:" in result.output
    assert "Yes" in result.output
    assert "Commands:" in result.output


def test_preset_info_not_installed(project_dir: Path) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)

    result = runner.invoke(app, ["preset", "info", "cypress"])
    assert result.exit_code == 0, result.output
    assert "Installed:" in result.output
    assert "No" in result.output
