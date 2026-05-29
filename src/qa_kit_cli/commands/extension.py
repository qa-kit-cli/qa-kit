"""`qakit extension *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
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


@app.command("add")
@app.command("install")
def add(
    extension_ref: str,
    priority: int = typer.Option(10, "--priority", help="Extension priority (lower = higher priority). Default: 10."),
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Add an extension (bundled ID, local --dev path, or --from URL)."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    source = from_url or dev or extension_ref
    manager = ExtensionManager(project_root)
    entry = manager.add(source, priority=priority)
    _reregister_active(project_root, qakit_dir)
    print_success(f"Added extension '{entry['id']}' (priority={priority}).")


@app.command("remove")
@app.command("uninstall")
def remove(
    extension_id: str,
    keep_config: bool = typer.Option(
        False, "--keep-config", help="Preserve extension config files (back them up instead of deleting)."
    ),
    force: bool = typer.Option(
        False, "--force", help="Skip confirmation and remove managed files immediately."
    ),
) -> None:
    """Remove an installed extension."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    manager = ExtensionManager(project_root)
    if manager.remove(extension_id, keep_config=keep_config, force=force):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Removed extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not installed.")


@app.command("update")
def update(
    extension_id: Optional[str] = typer.Argument(None, help="Extension to update (default: all)."),
) -> None:
    """Re-install an extension to pick up the latest bundled version."""
    manager = _manager()
    entries = manager.list()
    targets = [e for e in entries if extension_id is None or e.get("id") == extension_id]
    if not targets:
        print_warning(f"Extension '{extension_id}' is not installed." if extension_id else "No extensions installed.")
        return
    for e in targets:
        eid = str(e.get("id", ""))
        try:
            manager.add(eid)
            print_info(f"Updated extension '{eid}'.")
        except FileNotFoundError:
            print_warning(f"Extension source for '{eid}' not found — skipping.")
    print_success("Extension update complete.")


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
    bundled = manager.registry.list_bundled()
    rows: list[list[str]] = []
    for eid in bundled:
        if query and query.lower() not in eid.lower():
            continue
        rows.append([eid, "bundled", ""])
    if rows:
        print_table(["Extension", "Source", "Tags"], rows, title="Extension Search Results")
    else:
        print_info("No extensions found matching the query.")


@app.command("info")
def info(extension_id: str) -> None:
    """Show details about an extension."""
    import yaml

    manager = _manager()
    try:
        src = manager.registry.resolve(extension_id)
    except FileNotFoundError:
        print_warning(f"Extension '{extension_id}' not found.")
        raise typer.Exit(1)
    manifest_file = src / "extension.yml"
    if not manifest_file.exists():
        print_warning(f"No extension.yml found in '{src}'.")
        raise typer.Exit(1)
    data = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
    rows = [[k, str(v)] for k, v in data.items() if not isinstance(v, (list, dict))]
    print_table(["Field", "Value"], rows, title=f"Extension: {extension_id}")
    hooks = data.get("hooks", [])
    if hooks:
        print_info(f"Hooks: {', '.join(hooks)}")


@app.command("resolve")
def resolve(template_name: str) -> None:
    """Show the 4-layer template resolution stack for a given template name (includes extensions).

    Example: qakit extension resolve write.playwright.md
    """
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    resolver = TemplateResolver(qakit_dir)
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
