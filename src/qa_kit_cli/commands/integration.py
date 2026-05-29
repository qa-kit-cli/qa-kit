"""`qakit integration *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
from qa_kit_cli._integration_options import parse_integration_options
from qa_kit_cli.agents import CommandRegistrar, SkillRegistrar
from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations import get_integration, list_integrations
from qa_kit_cli.integrations.manifest import get_modified_files, uninstall_files
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage AI agent integrations.")


def _ctx() -> tuple[Path, Path]:
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    return project_root, qakit_dir


def _install_integration(
    project_root: Path,
    qakit_dir: Path,
    key: str,
    integration_options: str | None = None,
) -> int:
    int_opts = parse_integration_options(integration_options)
    skills_mode = bool(int_opts.get("skills", False))
    integration_cls = get_integration(key)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {key}")

    if skills_mode and integration_cls.supports_skills:
        installed = SkillRegistrar().install_for_integration(project_root, qakit_dir, key)
        mode = "skills"
    else:
        installed = CommandRegistrar().install_for_integration(project_root, qakit_dir, key)
        mode = "commands"

    state = IntegrationState.load(qakit_dir)
    meta = {"name": integration_cls.config.get("name", key), "mode": mode}
    if int_opts:
        meta["options"] = int_opts  # type: ignore[assignment]
    if not state.active_key:
        state.set_active(key)
    state.add(key, meta)
    state.save(qakit_dir)
    return len(installed)


@app.command("add")
@app.command("install")
def add(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
) -> None:
    """Install slash commands (or skills) for an integration."""
    project_root, qakit_dir = _ctx()
    count = _install_integration(project_root, qakit_dir, key, integration_options)
    print_success(f"Installed integration '{key}' ({count} files).")


@app.command("remove")
@app.command("uninstall")
def remove(
    key: str,
    force: bool = typer.Option(
        False, "--force", help="Remove even files that have been locally modified."
    ),
) -> None:
    """Remove an installed integration and its managed files."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        print_warning(f"Integration '{key}' is not installed.")
        return

    removed, skipped = uninstall_files(qakit_dir, key, force=force)
    if skipped:
        print_warning(
            f"{len(skipped)} locally-modified file(s) were preserved. "
            "Use --force to remove them."
        )

    # Also remove skills manifest if present
    removed_skills, _ = uninstall_files(qakit_dir, f"{key}.skills", force=force)
    removed += removed_skills

    state.remove(key)
    if state.active_key == key:
        state.active_key = next(iter(state.installed.keys()), "")
    state.save(qakit_dir)
    print_success(f"Removed integration '{key}' ({len(removed)} files removed).")


@app.command("switch")
def switch(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
) -> None:
    """Install (if needed) and make an integration active."""
    project_root, qakit_dir = _ctx()
    integration_cls = get_integration(key)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {key}")

    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        _install_integration(project_root, qakit_dir, key, integration_options)
        state = IntegrationState.load(qakit_dir)

    state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Switched active integration to '{key}'.")


@app.command("use")
def use(key: str) -> None:
    """Switch to an already-installed integration without reinstalling files."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        print_warning(
            f"Integration '{key}' is not installed. "
            "Use 'qakit integration install {key}' first."
        )
        raise typer.Exit(1)
    state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Active integration set to '{key}'.")


@app.command("list")
def list_cmd() -> None:
    """List installed and available integrations."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    available = {i.key: i for i in list_integrations()}
    rows: list[list[str]] = []
    for key, intg in sorted(available.items()):
        status = "installed" if state.is_installed(key) else "available"
        active = "active" if state.active_key == key else ""
        meta = state.installed.get(key, {})
        mode = str(meta.get("mode", ""))
        rows.append([key, intg.config.get("name", key), status, mode, active])
    print_table(["Key", "Name", "Status", "Mode", "Active"], rows, title="Integrations")


@app.command("upgrade")
def upgrade(
    key: Optional[str] = typer.Argument(None, help="Integration key to upgrade (default: all installed)."),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite locally-modified files.",
    ),
) -> None:
    """Reinstall command templates for installed integrations."""
    project_root, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.installed:
        print_warning("No installed integrations found.")
        return

    targets = [key] if key else list(state.installed.keys())
    for invalid in [k for k in targets if not state.is_installed(k)]:
        print_warning(f"Integration '{invalid}' is not installed — skipping.")
        targets = [k for k in targets if k != invalid]

    total = 0
    for k in targets:
        modified = get_modified_files(qakit_dir, k)
        if modified and not force:
            print_warning(
                f"Integration '{k}' has {len(modified)} locally-modified file(s). "
                "Use --force to overwrite."
            )
            continue
        meta = state.installed.get(k, {})
        skills_mode = meta.get("mode") == "skills"
        int_cls = get_integration(k)
        if skills_mode and int_cls and int_cls.supports_skills:
            installed = SkillRegistrar().install_for_integration(project_root, qakit_dir, k)
        else:
            installed = CommandRegistrar().install_for_integration(project_root, qakit_dir, k)
        total += len(installed)
        print_info(f"Refreshed '{k}': {len(installed)} files")

    print_success(f"Integration upgrade complete ({total} files refreshed).")
