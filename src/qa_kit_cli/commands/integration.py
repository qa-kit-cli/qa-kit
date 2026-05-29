"""`qakit integration *` commands."""

from __future__ import annotations

from pathlib import Path

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
from qa_kit_cli.agents import CommandRegistrar
from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations import get_integration, list_integrations
from qa_kit_cli.integrations.manifest import uninstall_files
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage AI agent integrations.")


def _ctx() -> tuple[Path, Path]:
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    return project_root, qakit_dir


@app.command("add")
def add(key: str) -> None:
    """Install slash commands for an integration."""
    integration = get_integration(key)
    if integration is None:
        raise typer.BadParameter(f"Unknown integration: {key}")
    project_root, qakit_dir = _ctx()
    registrar = CommandRegistrar()
    installed = registrar.install_for_integration(project_root, qakit_dir, key)

    state = IntegrationState.load(qakit_dir)
    state.add(key, {"name": integration.config.get("name", key)})
    if not state.active_key:
        state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Installed integration '{key}' ({len(installed)} files).")


@app.command("remove")
def remove(key: str) -> None:
    """Remove an installed integration and its managed files."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        print_warning(f"Integration '{key}' is not installed.")
        return

    removed = uninstall_files(qakit_dir, key)
    state.remove(key)
    if state.active_key == key:
        state.active_key = next(iter(state.installed.keys()), "")
    state.save(qakit_dir)
    print_success(f"Removed integration '{key}' ({len(removed)} files removed).")


@app.command("switch")
def switch(key: str) -> None:
    """Switch the active integration."""
    project_root, qakit_dir = _ctx()
    integration = get_integration(key)
    if integration is None:
        raise typer.BadParameter(f"Unknown integration: {key}")

    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        registrar = CommandRegistrar()
        registrar.install_for_integration(project_root, qakit_dir, key)
        state.add(key, {"name": integration.config.get("name", key)})
    state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Switched active integration to '{key}'.")


@app.command("list")
def list_cmd() -> None:
    """List installed and available integrations."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    available = {i.key: i for i in list_integrations()}
    rows: list[list[str]] = []
    for key, integration in sorted(available.items()):
        status = "installed" if state.is_installed(key) else "available"
        active = "active" if state.active_key == key else ""
        rows.append([key, integration.config.get("name", key), status, active])
    print_table(["Key", "Name", "Status", "Active"], rows, title="Integrations")


@app.command("upgrade")
def upgrade() -> None:
    """Reinstall command templates for all installed integrations."""
    project_root, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.installed:
        print_warning("No installed integrations found.")
        return
    registrar = CommandRegistrar()
    total = 0
    for key in state.installed.keys():
        installed = registrar.install_for_integration(project_root, qakit_dir, key)
        total += len(installed)
        print_info(f"Refreshed {key}: {len(installed)} files")
    print_success(f"Integration upgrade complete ({total} files refreshed).")

