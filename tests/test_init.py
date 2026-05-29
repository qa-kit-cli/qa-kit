from __future__ import annotations

from pathlib import Path
from unittest.mock import call, patch

import pytest
from typer.testing import CliRunner

from qa_kit_cli import app


def test_init_scaffolds_project(project_dir) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--here"])
    assert result.exit_code == 0, result.output
    assert (project_dir / ".qakit").is_dir()
    assert (project_dir / ".qakit" / "memory" / "qa-strategy.md").exists()
    assert (project_dir / ".qakit" / "integration.json").exists()
    assert (project_dir / ".claude" / "commands").is_dir()


def test_init_no_args_prompts_user(project_dir) -> None:
    runner = CliRunner()
    with (
        patch("qa_kit_cli.commands.init._is_interactive_stdin", return_value=True),
        patch("qa_kit_cli.commands.init.subprocess.run"),
    ):
        result = runner.invoke(app, ["init", "--ignore-agent-tools"], input="y\n")
    assert result.exit_code == 0, result.output
    assert "No project name given. Initialize QA Kit in the current directory?" in result.output


def test_init_no_args_ci_aborts(project_dir) -> None:
    runner = CliRunner()
    with patch("qa_kit_cli.commands.init._is_interactive_stdin", return_value=False):
        result = runner.invoke(app, ["init", "--ignore-agent-tools"])
    assert result.exit_code != 0
    assert "specify a project name, pass `.`, or use `--here` to init in" in result.output
    assert "the current directory" in result.output


def test_init_no_git_skips_git_operations(project_dir) -> None:
    runner = CliRunner()
    with patch("qa_kit_cli.commands.init.subprocess.run") as run_mock:
        result = runner.invoke(app, ["init", "--here", "--no-git", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    assert call(["git", "init"], cwd=project_dir, check=False) not in run_mock.call_args_list


def test_init_no_git_default_runs_git(project_dir) -> None:
    runner = CliRunner()
    with patch("qa_kit_cli.commands.init.subprocess.run") as run_mock:
        result = runner.invoke(app, ["init", "--here", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    assert call(["git", "init"], cwd=project_dir, check=False) in run_mock.call_args_list


def test_qakit_suite_env_var_sets_active_suite(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """QAKIT_SUITE env var stored as active_suite in config.json."""
    monkeypatch.setenv("QAKIT_SUITE", "login-flow")
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--here", "--no-git"])
    assert result.exit_code == 0, result.output
    from qa_kit_cli.project_config import ProjectConfig
    cfg = ProjectConfig.load(project_dir / ".qakit")
    assert cfg.active_suite is not None
    assert "login-flow" in cfg.active_suite


def test_cli_suite_flag_beats_env_var(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """--suite flag overrides QAKIT_SUITE env var."""
    monkeypatch.setenv("QAKIT_SUITE", "from-env")
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--here", "--no-git", "--suite", "from-flag"])
    assert result.exit_code == 0, result.output
    from qa_kit_cli.project_config import ProjectConfig
    cfg = ProjectConfig.load(project_dir / ".qakit")
    assert cfg.active_suite is not None
    assert "from-flag" in cfg.active_suite


def test_no_suite_active_suite_is_null(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Neither --suite nor QAKIT_SUITE → active_suite is None."""
    monkeypatch.delenv("QAKIT_SUITE", raising=False)
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--here", "--no-git"])
    assert result.exit_code == 0, result.output
    from qa_kit_cli.project_config import ProjectConfig
    cfg = ProjectConfig.load(project_dir / ".qakit")
    assert cfg.active_suite is None
