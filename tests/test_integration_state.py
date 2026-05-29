from __future__ import annotations

from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.shared_infra import ensure_project_layout


def test_integration_state_roundtrip(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    state = IntegrationState()
    state.add("claude", {"name": "Claude Code"})
    state.set_active("claude")
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert loaded.active_key == "claude"
    assert loaded.is_installed("claude")


def test_integration_state_default_active_key_is_empty() -> None:
    state = IntegrationState()
    assert state.active_key == ""


def test_integration_state_is_not_installed_for_unknown_key() -> None:
    state = IntegrationState()
    assert not state.is_installed("copilot")


def test_integration_state_add_multiple_integrations(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    state = IntegrationState()
    state.add("claude", {"name": "Claude Code"})
    state.add("copilot", {"name": "GitHub Copilot"})
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert loaded.is_installed("claude")
    assert loaded.is_installed("copilot")


def test_integration_state_remove(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    state = IntegrationState()
    state.add("claude", {"name": "Claude Code"})
    state.remove("claude")
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert not loaded.is_installed("claude")


def test_integration_state_remove_nonexistent_is_silent() -> None:
    state = IntegrationState()
    state.remove("never-added")  # must not raise
    assert not state.is_installed("never-added")


def test_integration_state_schema_version_is_current(project_dir) -> None:
    """Saved state should use current schema version (2)."""
    qakit_dir = ensure_project_layout(project_dir)
    state = IntegrationState()
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert loaded.schema_version == 2


def test_integration_state_set_active_changes_active_key(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    state = IntegrationState()
    state.add("claude", {})
    state.add("copilot", {})
    state.set_active("copilot")
    state.save(qakit_dir)

    loaded = IntegrationState.load(qakit_dir)
    assert loaded.active_key == "copilot"


def test_integration_state_loads_empty_file_gracefully(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    # No integration.json written — load_json returns {}
    loaded = IntegrationState.load(qakit_dir)
    assert loaded.active_key == ""
    assert loaded.installed == {}
