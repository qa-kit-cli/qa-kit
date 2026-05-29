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
from qa_kit_cli.project_config import ProjectConfig
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage AI agent integrations.")

_alias_notice_shown: set[str] = set()


def _ctx() -> tuple[Path, Path]:
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    return project_root, qakit_dir


def _install_integration(
    project_root: Path,
    qakit_dir: Path,
    key: str,
    integration_options: str | None = None,
    script: str | None = None,
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
        if skills_mode and not integration_cls.supports_skills:
            print_warning(
                f"Integration '{key}' does not support skills mode; falling back to commands."
            )
        installed = CommandRegistrar().install_for_integration(project_root, qakit_dir, key)
        mode = "commands"

    state = IntegrationState.load(qakit_dir)
    meta: dict = {"name": integration_cls.config.get("name", key), "mode": mode}
    if int_opts:
        meta["options"] = int_opts
    if script:
        meta["script"] = script

    # Persist script to project config when provided
    if script in ("sh", "ps"):
        cfg = ProjectConfig.load(qakit_dir)
        cfg.script = script
        cfg.save(qakit_dir)

    if not state.active_key:
        state.set_active(key)
    state.add(key, meta)
    state.save(qakit_dir)
    return len(installed)


def _install_command(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow installation even when another active integration exists and multi-install is unsafe.",
    ),
) -> None:
    """Install slash commands (or skills) for an integration."""
    project_root, qakit_dir = _ctx()
    integration_cls = get_integration(key)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {key}")

    state = IntegrationState.load(qakit_dir)

    # Multi-install safety check
    if (
        state.active_key
        and state.active_key != key
        and not integration_cls.multi_install_safe
        and not force
    ):
        print_warning(
            f"Integration '{key}' is not marked as multi-install safe and "
            f"'{state.active_key}' is already active. "
            "Use --force to install anyway."
        )
        raise typer.Exit(1)

    count = _install_integration(project_root, qakit_dir, key, integration_options)
    print_success(f"Installed integration '{key}' ({count} files).")


@app.command("install")
def install(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow installation even when another active integration exists and multi-install is unsafe.",
    ),
) -> None:
    """Install an AI agent integration."""
    _install_command(key, integration_options=integration_options, force=force)


@app.command("add")
def add_alias(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow installation even when another active integration exists and multi-install is unsafe.",
    ),
) -> None:
    """Alias for install."""
    if "integration.add" not in _alias_notice_shown:
        _alias_notice_shown.add("integration.add")
        print_info(
            "Tip: 'qakit integration add' is an alias for 'qakit integration install'.\n"
            "     Both work identically — 'install' is the preferred name going forward."
        )
    _install_command(key, integration_options=integration_options, force=force)


def _remove_command(
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


@app.command("uninstall")
def uninstall(
    key: str,
    force: bool = typer.Option(
        False, "--force", help="Remove even files that have been locally modified."
    ),
) -> None:
    """Uninstall an AI agent integration."""
    _remove_command(key, force=force)


@app.command("remove")
def remove_alias(
    key: str,
    force: bool = typer.Option(
        False, "--force", help="Remove even files that have been locally modified."
    ),
) -> None:
    """Alias for uninstall."""
    if "integration.remove" not in _alias_notice_shown:
        _alias_notice_shown.add("integration.remove")
        print_info(
            "Tip: 'qakit integration remove' is an alias for 'qakit integration uninstall'.\n"
            "     Both work identically — 'uninstall' is the preferred name going forward."
        )
    _remove_command(key, force=force)


@app.command("switch")
def switch(
    key: str,
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Agent-specific options, e.g. '--skills'."
    ),
    script: Optional[str] = typer.Option(
        None, "--script", help="Platform script type: 'sh' or 'ps'."
    ),
    force: bool = typer.Option(
        False, "--force", help="Force switch even if another integration is active."
    ),
) -> None:
    """Install (if needed) and make an integration active."""
    project_root, qakit_dir = _ctx()
    integration_cls = get_integration(key)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {key}")

    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        _install_integration(project_root, qakit_dir, key, integration_options, script)
        state = IntegrationState.load(qakit_dir)

    state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Switched active integration to '{key}'.")


@app.command("use")
def use(
    key: str,
    force: bool = typer.Option(
        False, "--force", help="Refresh managed shared templates for the integration."
    ),
) -> None:
    """Switch to an already-installed integration without reinstalling files."""
    project_root, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    if not state.is_installed(key):
        print_warning(
            f"Integration '{key}' is not installed. "
            f"Use 'qakit integration install {key}' first."
        )
        raise typer.Exit(1)

    if force:
        meta = state.installed.get(key, {})
        skills_mode = meta.get("mode") == "skills"
        int_cls = get_integration(key)
        if skills_mode and int_cls and int_cls.supports_skills:
            SkillRegistrar().install_for_integration(project_root, qakit_dir, key)
        else:
            CommandRegistrar().install_for_integration(project_root, qakit_dir, key)
        print_info(f"Refreshed managed templates for '{key}'.")

    state.set_active(key)
    state.save(qakit_dir)
    print_success(f"Active integration set to '{key}'.")


@app.command("list")
def list_cmd(
    catalog: bool = typer.Option(
        False, "--catalog", help="Show all catalog integrations (not just installed)."
    ),
) -> None:
    """List installed and available integrations."""
    _, qakit_dir = _ctx()
    state = IntegrationState.load(qakit_dir)
    available = {i.key: i for i in list_integrations()}
    rows: list[list[str]] = []
    if catalog:
        for key, intg in sorted(available.items()):
            integration_type = "skills+commands" if intg.supports_skills else "commands"
            installed = "yes" if state.is_installed(key) else "no"
            safe = "yes" if intg.multi_install_safe else "no"
            cli_required = "yes" if bool(intg.config.get("requires_cli")) else "no"
            rows.append([
                key,
                str(intg.config.get("name", key)),
                integration_type,
                installed,
                safe,
                cli_required,
            ])
        print_table(
            ["Key", "Name", "Type", "Installed", "Multi-safe", "CLI Required"],
            rows,
            title="Integration Catalog",
        )
        return

    for key, meta in sorted(state.installed.items()):
        intg = available.get(key)
        if intg is None:
            integration_type = str(meta.get("mode", "commands"))
            safe = "no"
            cli_required = "unknown"
            name = str(meta.get("name", key))
        else:
            integration_type = "skills+commands" if intg.supports_skills else "commands"
            safe = "yes" if intg.multi_install_safe else "no"
            cli_required = "yes" if bool(intg.config.get("requires_cli")) else "no"
            name = str(intg.config.get("name", key))
        active = "yes" if state.active_key == key else "no"
        rows.append([key, name, integration_type, active, safe, cli_required])

    print_table(
        ["Key", "Name", "Type", "Active", "Multi-safe", "CLI Required"],
        rows,
        title="Installed Integrations",
    )


@app.command("upgrade")
def upgrade(
    key: Optional[str] = typer.Argument(None, help="Integration key to upgrade (default: all installed)."),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite locally-modified files.",
    ),
    script: Optional[str] = typer.Option(
        None, "--script", help="Update script type: 'sh' or 'ps'."
    ),
    integration_options: Optional[str] = typer.Option(
        None, "--integration-options", help="Update integration options, e.g. '--skills'."
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
        # Apply new options/script if provided
        if integration_options is not None:
            int_opts = parse_integration_options(integration_options)
            meta["options"] = int_opts  # type: ignore[assignment]
            skills_mode = bool(int_opts.get("skills", False))
            meta["mode"] = "skills" if skills_mode else "commands"
        if script in ("sh", "ps"):
            meta["script"] = script
            cfg = ProjectConfig.load(qakit_dir)
            cfg.script = script
            cfg.save(qakit_dir)
        state.add(k, meta)

        skills_mode = meta.get("mode") == "skills"
        int_cls = get_integration(k)
        if skills_mode and int_cls and int_cls.supports_skills:
            installed = SkillRegistrar().install_for_integration(project_root, qakit_dir, k)
        else:
            installed = CommandRegistrar().install_for_integration(project_root, qakit_dir, k)
        total += len(installed)
        print_info(f"Refreshed '{k}': {len(installed)} files")

    state.save(qakit_dir)
    print_success(f"Integration upgrade complete ({total} files refreshed).")
