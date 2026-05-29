"""Tests for new qakit init flags: --no-git, --branch-numbering, platform-aware script, init-options.json."""

from __future__ import annotations

import json
import platform
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from qa_kit_cli.__init__ import app
from qa_kit_cli.shared_infra import ensure_project_layout


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# Platform-aware script default
# ---------------------------------------------------------------------------

def test_init_script_defaults_to_ps_on_windows(project_dir: Path, runner: CliRunner) -> None:
    with patch("qa_kit_cli.commands.init.platform.system", return_value="Windows"):
        result = runner.invoke(app, ["init", "--here", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    qakit_dir = project_dir / ".qakit"
    cfg_file = qakit_dir / "config.json"
    assert cfg_file.exists()
    cfg = json.loads(cfg_file.read_text())
    assert cfg["script"] == "ps"


def test_init_script_defaults_to_sh_on_linux(project_dir: Path, runner: CliRunner) -> None:
    with patch("qa_kit_cli.commands.init.platform.system", return_value="Linux"):
        result = runner.invoke(app, ["init", "--here", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    qakit_dir = project_dir / ".qakit"
    cfg = json.loads((qakit_dir / "config.json").read_text())
    assert cfg["script"] == "sh"


def test_init_explicit_script_overrides_default(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["init", "--here", "--script", "sh", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    qakit_dir = project_dir / ".qakit"
    cfg = json.loads((qakit_dir / "config.json").read_text())
    assert cfg["script"] == "sh"


# ---------------------------------------------------------------------------
# --no-git
# ---------------------------------------------------------------------------

def test_init_no_git_flag_accepted(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["init", "--here", "--no-git", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    # init-options.json should record no_git=True
    opts = json.loads((project_dir / ".qakit" / "init-options.json").read_text())
    assert opts["no_git"] is True


# ---------------------------------------------------------------------------
# --branch-numbering
# ---------------------------------------------------------------------------

def test_init_branch_numbering_sequential(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["init", "--here", "--branch-numbering", "sequential", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    cfg = json.loads((project_dir / ".qakit" / "config.json").read_text())
    assert cfg["branch_numbering"] == "sequential"


def test_init_branch_numbering_timestamp(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["init", "--here", "--branch-numbering", "timestamp", "--ignore-agent-tools"])
    assert result.exit_code == 0, result.output
    cfg = json.loads((project_dir / ".qakit" / "config.json").read_text())
    assert cfg["branch_numbering"] == "timestamp"


def test_init_branch_numbering_invalid_rejected(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["init", "--here", "--branch-numbering", "weekly", "--ignore-agent-tools"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# init-options.json snapshot
# ---------------------------------------------------------------------------

def test_init_writes_init_options_json(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(
        app,
        ["init", "--here", "--branch-numbering", "timestamp", "--no-git", "--ignore-agent-tools"],
    )
    assert result.exit_code == 0, result.output
    opts_file = project_dir / ".qakit" / "init-options.json"
    assert opts_file.exists()
    opts = json.loads(opts_file.read_text())
    assert opts["schema_version"] == 1
    assert opts["branch_numbering"] == "timestamp"
    assert opts["no_git"] is True


# ---------------------------------------------------------------------------
# --preset repeatable
# ---------------------------------------------------------------------------

def test_init_repeatable_preset_flag(project_dir: Path, runner: CliRunner) -> None:
    result = runner.invoke(
        app,
        ["init", "--here", "--preset", "playwright", "--preset", "cypress", "--ignore-agent-tools"],
    )
    assert result.exit_code == 0, result.output
    presets_dir = project_dir / ".qakit" / "presets"
    installed = [p.name for p in presets_dir.iterdir() if p.is_dir()]
    assert "playwright" in installed
    assert "cypress" in installed
