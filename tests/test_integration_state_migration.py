"""Tests for integration state schema migration (v1 → v2) and multi-install safety."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from qa_kit_cli.__init__ import app
from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations.claude import ClaudeIntegration
from qa_kit_cli.integrations.codex import CodexIntegration
from qa_kit_cli.integrations.generic import GenericIntegration
from qa_kit_cli.shared_infra import ensure_project_layout


# ---------------------------------------------------------------------------
# Schema migration
# ---------------------------------------------------------------------------

def test_load_v1_schema_migrates_to_v2(qakit_dir: Path) -> None:
    state_file = qakit_dir / "integration.json"
    v1_data = {
        "schema_version": 1,
        "active_key": "claude",
        "installed": {
            "claude": {"mode": "commands", "name": "Claude Code"},
            "codex": {"mode": "skills", "name": "Codex CLI"},
        },
    }
    state_file.write_text(json.dumps(v1_data))
    loaded = IntegrationState.load(qakit_dir)
    assert loaded.schema_version == 2
    assert loaded.active_key == "claude"
    assert "claude" in loaded.installed
    assert "codex" in loaded.installed


def test_load_unversioned_legacy_migrates(qakit_dir: Path) -> None:
    state_file = qakit_dir / "integration.json"
    legacy = {
        "active_key": "codex",
        "installed": {"codex": {"mode": "commands"}},
    }
    state_file.write_text(json.dumps(legacy))
    loaded = IntegrationState.load(qakit_dir)
    assert loaded.active_key == "codex"
    assert loaded.is_installed("codex")
    assert loaded.schema_version == 2


def test_saved_state_uses_new_schema(qakit_dir: Path) -> None:
    state = IntegrationState()
    state.add("claude", {"mode": "commands"})
    state.set_active("claude")
    state.save(qakit_dir)

    raw = json.loads((qakit_dir / "integration.json").read_text())
    assert raw["schema_version"] == 2
    assert raw["active_integration"] == "claude"
    assert "claude" in raw["installed_integrations"]
    assert "claude" in raw["integration_settings"]


def test_v2_round_trip(qakit_dir: Path) -> None:
    state = IntegrationState()
    state.add("claude", {"mode": "skills"})
    state.add("codex", {"mode": "commands"})
    state.set_active("codex")
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert loaded.active_key == "codex"
    assert set(loaded.installed.keys()) == {"claude", "codex"}


# ---------------------------------------------------------------------------
# multi_install_safe
# ---------------------------------------------------------------------------

def test_claude_is_multi_install_safe() -> None:
    assert ClaudeIntegration.multi_install_safe is True


def test_codex_is_multi_install_safe() -> None:
    assert CodexIntegration.multi_install_safe is True


def test_generic_is_not_multi_install_safe() -> None:
    assert GenericIntegration.multi_install_safe is False


# ---------------------------------------------------------------------------
# install refuses unsafe multi-install
# ---------------------------------------------------------------------------

def test_install_refuses_unsafe_multi_install(project_dir: Path) -> None:
    runner = CliRunner()
    qakit_dir = ensure_project_layout(project_dir)

    # First install claude (multi_install_safe=True)
    runner.invoke(app, ["integration", "install", "claude"])
    # Then try to install generic (multi_install_safe=False) without --force
    result = runner.invoke(app, ["integration", "install", "generic"])
    assert result.exit_code != 0
    assert "not marked as multi-install safe" in result.output or \
           "multi-install" in result.output.lower()


def test_install_unsafe_with_force_succeeds(project_dir: Path) -> None:
    runner = CliRunner()
    qakit_dir = ensure_project_layout(project_dir)

    runner.invoke(app, ["integration", "install", "claude"])
    result = runner.invoke(app, ["integration", "install", "generic", "--force"])
    assert result.exit_code == 0, result.output


def test_install_safe_integration_does_not_need_force(project_dir: Path) -> None:
    runner = CliRunner()
    qakit_dir = ensure_project_layout(project_dir)

    runner.invoke(app, ["integration", "install", "claude"])
    result = runner.invoke(app, ["integration", "install", "codex"])
    # Both are multi_install_safe, so should succeed without --force
    assert result.exit_code == 0, result.output
