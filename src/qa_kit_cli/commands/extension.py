"""`qakit extension *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel

from qa_kit_cli._console import console, print_info, print_success, print_table, print_warning
from qa_kit_cli.catalogs import ExtensionCatalogStack
from qa_kit_cli.extensions import ExtensionManager
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.template_resolver import TemplateResolver

app = typer.Typer(help="Manage QA Kit extensions.")
catalog_app = typer.Typer(help="Manage extension catalogs.")
app.add_typer(catalog_app, name="catalog")


def _manager() -> ExtensionManager:
    project_root = Path.cwd()
    ensure_project_layout(project_root)
    return ExtensionManager(project_root)


def _reregister_active(project_root: Path, qakit_dir: Path) -> None:
    """Reinstall commands for the active integration so extension templates apply."""
    from qa_kit_cli.agents import CommandRegistrar, SkillRegistrar
    from qa_kit_cli.integration_state import IntegrationState
    from qa_kit_cli.integrations import get_integration

    state = IntegrationState.load(qakit_dir)
    key = state.active_key
    if not key:
        return
    meta = state.installed.get(key, {})
    skills_mode = meta.get("mode") == "skills"
    int_cls = get_integration(key)
    if skills_mode and int_cls and int_cls.supports_skills:
        SkillRegistrar().install_for_integration(project_root, qakit_dir, key)
    else:
        CommandRegistrar().install_for_integration(project_root, qakit_dir, key)


_ext_alias_shown: set[str] = set()


def _do_add_extension(
    extension_ref: str,
    priority: int,
    dev: Optional[str],
    from_url: Optional[str],
) -> None:
    """Shared implementation for install and add extension commands."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    source = from_url or dev or extension_ref
    manager = ExtensionManager(project_root)
    entry = manager.add(source, priority=priority)
    _reregister_active(project_root, qakit_dir)
    print_success(f"Added extension '{entry['id']}' (priority={priority}).")


def _do_remove_extension(
    extension_id: str,
    keep_config: bool,
    force: bool,
) -> None:
    """Shared implementation for uninstall and remove extension commands."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    manager = ExtensionManager(project_root)
    if manager.remove(extension_id, keep_config=keep_config, force=force):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Removed extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not installed.")


@app.command("install")
def install_ext(
    extension_ref: str,
    priority: int = typer.Option(10, "--priority", help="Extension priority (lower = higher priority). Default: 10."),
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Install an extension (bundled ID, local --dev path, or --from URL)."""
    _do_add_extension(extension_ref, priority, dev, from_url)


@app.command("add")
def add(
    extension_ref: str,
    priority: int = typer.Option(10, "--priority", help="Extension priority (lower = higher priority). Default: 10."),
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Alias for install."""
    if "extension.add" not in _ext_alias_shown:
        _ext_alias_shown.add("extension.add")
        print_info(
            "Tip: 'qakit extension add' is an alias for 'qakit extension install'.\n"
            "     Both work identically — 'install' is the preferred name going forward."
        )
    _do_add_extension(extension_ref, priority, dev, from_url)


@app.command("uninstall")
def uninstall_ext(
    extension_id: str,
    keep_config: bool = typer.Option(
        False, "--keep-config", help="Preserve extension config files (back them up instead of deleting)."
    ),
    force: bool = typer.Option(
        False, "--force", help="Skip confirmation and remove managed files immediately."
    ),
) -> None:
    """Remove an installed extension."""
    _do_remove_extension(extension_id, keep_config, force)


@app.command("remove")
def remove(
    extension_id: str,
    keep_config: bool = typer.Option(
        False, "--keep-config", help="Preserve extension config files (back them up instead of deleting)."
    ),
    force: bool = typer.Option(
        False, "--force", help="Skip confirmation and remove managed files immediately."
    ),
) -> None:
    """Alias for uninstall."""
    if "extension.remove" not in _ext_alias_shown:
        _ext_alias_shown.add("extension.remove")
        print_info(
            "Tip: 'qakit extension remove' is an alias for 'qakit extension uninstall'.\n"
            "     Both work identically — 'uninstall' is the preferred name going forward."
        )
    _do_remove_extension(extension_id, keep_config, force)


@app.command("update")
def update(
    extension_id: str = typer.Argument(..., help="Extension to update."),
    force: bool = typer.Option(False, "--force", help="Overwrite locally modified templates."),
) -> None:
    """Update an installed extension to the latest available version."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    manager = ExtensionManager(project_root)
    try:
        result = manager.update(extension_id, force=force)
    except FileNotFoundError:
        print_warning(f"Extension '{extension_id}' is not installed.")
        raise typer.Exit(1)

    if result.get("already_latest"):
        print_info("Already at latest version")
        return

    _reregister_active(project_root, qakit_dir)
    print_success(
        f"Updated {extension_id} from v{result['old_version']} \u2192 v{result['new_version']}: "
        f"{result['updated_templates']} templates updated"
    )


@app.command("list")
def list_cmd(
    available: bool = typer.Option(False, "--available", help="Show catalog/bundled extensions not yet installed."),
    all_exts: bool = typer.Option(False, "--all", help="Show both installed and available extensions."),
) -> None:
    """List installed (and optionally available) extensions."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    manager = ExtensionManager(project_root)
    installed_entries = manager.list()
    installed_ids = {e.get("id") for e in installed_entries}

    rows: list[list[str]] = []

    if not available:
        for e in installed_entries:
            ext_path = qakit_dir / "extensions" / str(e.get("id", ""))
            # Count commands from extension.yml if available
            cmd_count = "-"
            hook_count = "-"
            try:
                import yaml as _yaml
                mf = ext_path / "extension.yml"
                if mf.exists():
                    d = _yaml.safe_load(mf.read_text(encoding="utf-8")) or {}
                    cmd_count = str(len(d.get("commands", {})))
                    hook_count = str(len(d.get("hooks", [])))
            except Exception:
                pass
            rows.append([
                str(e.get("id", "")),
                str(e.get("name", "")),
                str(e.get("version", "")),
                str(e.get("priority", 10)),
                "enabled" if e.get("enabled", True) else "disabled",
                cmd_count,
                hook_count,
            ])
        print_table(["ID", "Name", "Version", "Priority", "Status", "Commands", "Hooks"], rows, title="Installed Extensions")
        return

    # --available or --all: show bundled extensions
    bundled = manager.registry.list_bundled()
    for bid in bundled:
        status = "installed" if bid in installed_ids else "available"
        if available and status == "installed":
            continue
        rows.append([bid, "", "", "", status, "", ""])
    print_table(["ID", "Name", "Version", "Priority", "Status", "Commands", "Hooks"], rows, title="Extensions")


@app.command("enable")
def enable(extension_id: str) -> None:
    """Enable an extension."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if _manager().set_enabled(extension_id, True):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Enabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("disable")
def disable(extension_id: str) -> None:
    """Disable an extension without removing it."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if _manager().set_enabled(extension_id, False):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Disabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("set-priority")
def set_priority(extension_id: str, value: int) -> None:
    """Set the priority of an extension (lower = higher priority in hooks)."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if _manager().set_priority(extension_id, value):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Set extension '{extension_id}' priority to {value}.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("search")
def search(
    query: Optional[str] = typer.Argument(None),
    tag: Optional[str] = typer.Option(None, "--tag"),
    author: Optional[str] = typer.Option(None, "--author"),
    verified: bool = typer.Option(False, "--verified"),
) -> None:
    """Search available extensions across active catalogs."""
    manager = _manager()
    stack = ExtensionCatalogStack(Path.cwd(), include_community=True)
    entries = stack.search(query or "")
    if stack.last_remote_failed:
        console.print("[yellow]Using bundled catalog (remote fetch failed)[/yellow]")

    installed_ids = {str(e.get("id", "")) for e in manager.list()}
    rows: list[list[str]] = []
    for item in entries:
        if tag:
            tags = item.get("tags", [])
            if isinstance(tags, list):
                if tag not in [str(t) for t in tags]:
                    continue
            elif tag != str(tags):
                continue
        if author and str(item.get("author", "")).lower() != author.lower():
            continue
        if verified and not bool(item.get("verified", False)):
            continue
        eid = str(item.get("id", ""))
        rows.append(
            [
                eid,
                str(item.get("name", "")),
                str(item.get("version", "")),
                str(item.get("description", "")),
                "Yes" if eid in installed_ids else "No",
            ]
        )
    if rows:
        print_table(["ID", "Name", "Version", "Description", "Installed"], rows, title="Extension Search Results")
    else:
        print_info("No extensions found matching the query.")


@app.command("info")
def info(extension_id: str) -> None:
    """Show details about an extension."""
    import yaml

    manager = _manager()
    stack = ExtensionCatalogStack(Path.cwd(), include_community=True)
    catalog_entry = stack.get(extension_id)
    installed_entry = next((e for e in manager.list() if str(e.get("id", "")) == extension_id), None)

    data: dict = {}
    source_label = "catalog"
    source_ref = str(catalog_entry.get("_source_ref", "")) if catalog_entry else ""
    manifest_path: Path | None = None

    if installed_entry:
        manifest_path = Path.cwd() / ".qakit" / "extensions" / extension_id / "extension.yml"
    else:
        try:
            src = manager.registry.resolve(extension_id)
            manifest_path = src / "extension.yml"
            if "extensions" in str(src):
                source_label = "bundled"
                source_ref = "bundled"
        except FileNotFoundError:
            manifest_path = None

    if manifest_path and manifest_path.exists():
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    elif catalog_entry:
        data = dict(catalog_entry)
    else:
        print_warning(f"Extension '{extension_id}' not found.")
        raise typer.Exit(1)

    hooks = data.get("hooks", [])
    commands = data.get("commands", {})
    if isinstance(commands, dict):
        command_list = list(commands.keys())
    elif isinstance(commands, list):
        command_list = [str(c) for c in commands]
    else:
        command_list = []

    if installed_entry:
        source_label = "catalog"
        source_ref = str(installed_entry.get("source", ""))

    if source_ref.startswith("http://") or source_ref.startswith("https://"):
        source_display = source_ref
    elif source_ref:
        source_display = "bundled"
    else:
        source_display = source_label

    panel_text = (
        f"Name:        {data.get('name', extension_id)}\n"
        f"ID:          {data.get('id', extension_id)}\n"
        f"Version:     {data.get('version', '')}\n"
        f"Author:      {data.get('author', '')}\n"
        f"Description: {data.get('description', '')}\n"
        f"Hooks:       {', '.join(str(h) for h in hooks) if hooks else '-'}\n"
        f"Commands:    {', '.join(command_list) if command_list else '-'}\n"
        f"Installed:   {'Yes' if installed_entry else 'No'}\n"
        f"Source:      {source_display}"
    )
    console.print(Panel(panel_text, title=f"Extension: {extension_id}", border_style="cyan"))


@app.command("resolve")
def resolve(
    template_name: str,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show all 4 layers, not just the winner."
    ),
) -> None:
    """Show the 4-layer template resolution stack for a given template name (includes extensions).

    Example: qakit extension resolve write.playwright.md
    """
    from rich import box
    from rich.table import Table

    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    resolver = TemplateResolver(qakit_dir)

    if verbose:
        results = resolver.resolve_with_trace(template_name)
        table = Table(
            title=f"Resolution stack: {template_name}",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
        )
        table.add_column("Layer", justify="center")
        table.add_column("Source")
        table.add_column("Template path")
        table.add_column("Status")

        for r in results:
            path_str = str(r.template_path) if r.template_path else "—"
            if r.wins:
                status = "WINS"
            elif r.template_path is not None:
                status = "skipped"
            else:
                status = "no file"
            table.add_row(str(r.layer_number), r.layer_label, path_str, status)
        console.print(table)
        return

    stack = resolver.resolve_stack(template_name)
    if not stack:
        print_warning(f"Template '{template_name}' was not found in any layer.")
        raise typer.Exit(1)

    rows: list[list[str]] = []
    for layer, path, wins in stack:
        winner = "WINS" if wins else ""
        rows.append([layer, str(path.relative_to(project_root) if path.is_relative_to(project_root) else path), winner])
    print_table(["Layer", "Path", ""], rows, title=f"Resolution stack: {template_name}")


# --- catalog subcommands ---

@catalog_app.command("list")
def catalog_list() -> None:
    """List active extension catalogs."""
    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "extension-catalogs.yml"
    if not catalog_file.exists():
        print_info("No project-level extension catalog configured (.qakit/extension-catalogs.yml).")
        return
    import yaml
    data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs = data.get("catalogs", [])
    rows = [[c.get("name", ""), c.get("url", ""), str(c.get("priority", ""))] for c in catalogs]
    print_table(["Name", "URL", "Priority"], rows, title="Extension Catalogs")


@catalog_app.command("add")
def catalog_add(
    url: str,
    name: Optional[str] = typer.Option(None, "--name"),
    priority: int = typer.Option(50, "--priority"),
    install_allowed: bool = typer.Option(False, "--install-allowed"),
) -> None:
    """Add an extension catalog URL."""
    import yaml

    project_root = Path.cwd()
    ensure_project_layout(project_root)
    catalog_file = project_root / ".qakit" / "extension-catalogs.yml"
    data: dict = {}
    if catalog_file.exists():
        data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs: list = data.get("catalogs", [])
    catalogs.append({"name": name or url, "url": url, "priority": priority, "install_allowed": install_allowed})
    data["catalogs"] = catalogs
    catalog_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    print_success(f"Added extension catalog '{name or url}'.")


@catalog_app.command("remove")
def catalog_remove(name: str) -> None:
    """Remove an extension catalog by name."""
    import yaml

    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "extension-catalogs.yml"
    if not catalog_file.exists():
        print_warning("No catalog file found.")
        return
    data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    before = len(data.get("catalogs", []))
    data["catalogs"] = [c for c in data.get("catalogs", []) if c.get("name") != name]
    catalog_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    if len(data["catalogs"]) < before:
        print_success(f"Removed catalog '{name}'.")
    else:
        print_warning(f"Catalog '{name}' not found.")
