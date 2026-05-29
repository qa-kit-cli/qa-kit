from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.shared_infra import ensure_project_layout


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_integration_aliases_resolve(project_dir: Path, runner: CliRunner) -> None:
    ensure_project_layout(project_dir)
    with patch("qa_kit_cli.commands.integration._install_integration", return_value=1) as install_mock:
        add_result = runner.invoke(app, ["integration", "add", "claude"])
        install_result = runner.invoke(app, ["integration", "install", "claude"])

    assert add_result.exit_code == 0, add_result.output
    assert install_result.exit_code == 0, install_result.output
    assert install_mock.call_count == 2
    assert install_mock.call_args_list[0].args[2] == "claude"
    assert install_mock.call_args_list[1].args[2] == "claude"


def test_integration_use_sets_default(project_dir: Path, runner: CliRunner) -> None:
    ensure_project_layout(project_dir)

    add_claude = runner.invoke(app, ["integration", "install", "claude"])
    assert add_claude.exit_code == 0, add_claude.output
    add_codex = runner.invoke(app, ["integration", "install", "codex"])
    assert add_codex.exit_code == 0, add_codex.output

    result = runner.invoke(app, ["integration", "use", "codex"])
    assert result.exit_code == 0, result.output

    state = json.loads((project_dir / ".qakit" / "integration.json").read_text(encoding="utf-8"))
    assert state.get("active_integration") == "codex"


def test_integration_list_catalog_flag(project_dir: Path, runner: CliRunner) -> None:
    ensure_project_layout(project_dir)

    result = runner.invoke(app, ["integration", "list", "--catalog"])
    assert result.exit_code == 0, result.output
    assert "Integration Catalog" in result.output
    assert "Installed" in result.output
    assert "claude" in result.output
