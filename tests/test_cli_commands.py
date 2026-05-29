"""CliRunner integration tests for all qakit subcommand groups."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.shared_infra import ensure_project_layout


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# qakit integration *
# ---------------------------------------------------------------------------


class TestIntegrationCommands:
    def test_add_installs_commands(self, project_dir: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["integration", "add", "claude"])
        assert result.exit_code == 0, result.output
        assert (project_dir / ".claude" / "commands").is_dir()

    def test_add_unknown_key_exits_nonzero(self, project_dir: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["integration", "add", "does-not-exist"])
        assert result.exit_code != 0

    def test_list_shows_available_integrations(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["integration", "list"])
        assert result.exit_code == 0, result.output
        assert "claude" in result.output

    def test_remove_installed_integration(self, project_dir: Path, runner: CliRunner) -> None:
        runner.invoke(app, ["integration", "add", "claude"])
        result = runner.invoke(app, ["integration", "remove", "claude"])
        assert result.exit_code == 0, result.output
        assert "Removed" in result.output

    def test_remove_noninstalled_warns(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["integration", "remove", "copilot"])
        assert result.exit_code == 0
        assert "not installed" in result.output

    def test_switch_installs_and_activates(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["integration", "switch", "copilot"])
        assert result.exit_code == 0, result.output
        assert "copilot" in result.output
        assert (project_dir / ".github" / "copilot-instructions").is_dir()

    def test_upgrade_refreshes_files(self, project_dir: Path, runner: CliRunner) -> None:
        runner.invoke(app, ["integration", "add", "claude"])
        result = runner.invoke(app, ["integration", "upgrade"])
        assert result.exit_code == 0, result.output
        assert "complete" in result.output.lower() or "refresh" in result.output.lower()

    def test_upgrade_warns_when_nothing_installed(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["integration", "upgrade"])
        assert result.exit_code == 0
        assert "No installed" in result.output


# ---------------------------------------------------------------------------
# qakit extension *
# ---------------------------------------------------------------------------


class TestExtensionCommands:
    def test_add_known_extension(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["extension", "add", "git"])
        assert result.exit_code == 0, result.output
        assert "git" in result.output

    def test_list_shows_added_extension(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["extension", "add", "git"])
        result = runner.invoke(app, ["extension", "list"])
        assert result.exit_code == 0, result.output
        assert "git" in result.output

    def test_disable_and_enable(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["extension", "add", "git"])

        r_disable = runner.invoke(app, ["extension", "disable", "git"])
        assert r_disable.exit_code == 0, r_disable.output
        assert "Disabled" in r_disable.output

        r_enable = runner.invoke(app, ["extension", "enable", "git"])
        assert r_enable.exit_code == 0, r_enable.output
        assert "Enabled" in r_enable.output

    def test_enable_nonexistent_warns(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["extension", "enable", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_remove_extension(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["extension", "add", "git"])
        result = runner.invoke(app, ["extension", "remove", "git"])
        assert result.exit_code == 0, result.output
        assert "Removed" in result.output

    def test_remove_noninstalled_warns(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["extension", "remove", "git"])
        assert result.exit_code == 0
        assert "not installed" in result.output


# ---------------------------------------------------------------------------
# qakit preset *
# ---------------------------------------------------------------------------


class TestPresetCommands:
    def test_add_known_preset(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["preset", "add", "playwright"])
        assert result.exit_code == 0, result.output
        assert "playwright" in result.output

    def test_list_shows_added_preset(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["preset", "add", "playwright"])
        result = runner.invoke(app, ["preset", "list"])
        assert result.exit_code == 0, result.output
        # Rich may truncate "playwright" → "playwrig…" in narrow terminal columns
        assert "playwrig" in result.output

    def test_priority_updates_value(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["preset", "add", "playwright"])
        result = runner.invoke(app, ["preset", "priority", "playwright", "3"])
        assert result.exit_code == 0, result.output
        assert "3" in result.output

    def test_priority_nonexistent_warns(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["preset", "priority", "nonexistent", "1"])
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_disable_and_enable(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["preset", "add", "playwright"])

        r_dis = runner.invoke(app, ["preset", "disable", "playwright"])
        assert r_dis.exit_code == 0, r_dis.output
        assert "Disabled" in r_dis.output

        r_en = runner.invoke(app, ["preset", "enable", "playwright"])
        assert r_en.exit_code == 0, r_en.output
        assert "Enabled" in r_en.output

    def test_remove_preset(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        runner.invoke(app, ["preset", "add", "playwright"])
        result = runner.invoke(app, ["preset", "remove", "playwright"])
        assert result.exit_code == 0, result.output
        assert "Removed" in result.output

    def test_remove_noninstalled_warns(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["preset", "remove", "playwright"])
        assert result.exit_code == 0
        assert "not installed" in result.output


# ---------------------------------------------------------------------------
# qakit workflow *
# ---------------------------------------------------------------------------


class TestWorkflowCommands:
    def test_list_shows_bundled_workflow(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["workflow", "list"])
        assert result.exit_code == 0, result.output
        assert "qakit" in result.output

    def test_run_bundled_workflow_succeeds(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["workflow", "run", "qakit"])
        assert result.exit_code == 0, result.output
        assert "completed" in result.output.lower()

    def test_run_unknown_workflow_exits_nonzero(self, project_dir: Path, runner: CliRunner) -> None:
        ensure_project_layout(project_dir)
        result = runner.invoke(app, ["workflow", "run", "nonexistent-workflow"])
        assert result.exit_code != 0
