from __future__ import annotations

from typer.testing import CliRunner

from qa_kit_cli import app


def test_init_scaffolds_project(project_dir) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output
    assert (project_dir / ".qakit").is_dir()
    assert (project_dir / ".qakit" / "memory" / "qa-strategy.md").exists()
    assert (project_dir / ".qakit" / "integration.json").exists()
    assert (project_dir / ".claude" / "commands").is_dir()

