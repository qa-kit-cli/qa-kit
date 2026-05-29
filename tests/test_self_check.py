from __future__ import annotations

import pytest
from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli._version import __version__


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_self_check_up_to_date(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "qa_kit_cli.safe_fetch_json",
        lambda url, default=None: {"info": {"version": __version__}},
    )
    result = runner.invoke(app, ["self", "check"])
    assert result.exit_code == 0, result.output
    assert f"qa-kit-cli is up to date ({__version__})" in result.output
    assert "qa_lifecycle_commands" in result.output


def test_self_check_update_available(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "qa_kit_cli.safe_fetch_json",
        lambda url, default=None: {"info": {"version": "9.9.9"}},
    )
    result = runner.invoke(app, ["self", "check"])
    assert result.exit_code == 0, result.output
    assert "Update available" in result.output
    assert "qakit self update" in result.output


def test_self_check_network_failure_graceful(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("qa_kit_cli.safe_fetch_json", lambda url, default=None: None)
    result = runner.invoke(app, ["self", "check"])
    assert result.exit_code == 0, result.output
    assert "Could not fetch latest version from PyPI." in result.output
    assert "Runtime" in result.output
