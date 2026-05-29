from __future__ import annotations

from unittest.mock import call, patch

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
