"""Resolve integration options and invoke command separator logic."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations import get_integration


def resolve_active_integration(qakit_dir: Path) -> str | None:
    """Return the active integration key, or None if none is set."""
    state = IntegrationState.load(qakit_dir)
    return state.active_key or None


def get_commands_dir_for_active(qakit_dir: Path) -> Path | None:
    """Return the commands directory path for the currently active integration."""
    key = resolve_active_integration(qakit_dir)
    if not key:
        return None
    integration = get_integration(key)
    if not integration:
        return None
    project_root = qakit_dir.parent
    folder = integration.config.get("folder", "")
    if not folder:
        return None
    return project_root / folder
