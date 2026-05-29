"""Tests for `qakit version --features --json` and root --version/-V aliases."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from qa_kit_cli.__init__ import app
from qa_kit_cli._version import __version__


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_version_command_shows_version(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_version_features_table(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version", "--features"])
    assert result.exit_code == 0
    assert "qa_lifecycle_commands" in result.output
    assert "skills_mode" in result.output
    assert "workflow_engine" in result.output


def test_version_features_json_is_valid(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version", "--features", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "version" in payload
    assert "features" in payload
    features = payload["features"]
    required_flags = {
        "qa_lifecycle_commands",
        "skills_mode",
        "preset_resolution",
        "extension_resolution",
        "workflow_engine",
        "catalog_stack",
        "integration_multi_install_safety",
        "machine_readable_version",
    }
    assert required_flags.issubset(set(features.keys()))
    assert all(isinstance(v, bool) for v in features.values())


def test_version_features_json_version_matches(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version", "--features", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["version"] == __version__


def test_root_version_flag(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_root_version_short_flag(runner: CliRunner) -> None:
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert __version__ in result.output
