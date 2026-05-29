"""`qakit extension *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
from qa_kit_cli.extensions import ExtensionManager
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage QA Kit extensions.")
catalog_app = typer.Typer(help="Manage extension catalogs.")
app.add_typer(catalog_app, name="catalog")


def _manager() -> ExtensionManager:
    project_root = Path.cwd()
    ensure_project_layout(project_root)
    return ExtensionManager(project_root)


@app.command("add")
@app.command("install")
def add(extension_ref: str) -> None:
    """Add an extension."""
    entry = _manager().add(extension_ref)
    print_success(f"Added extension '{entry['id']}'.")


@app.command("remove")
@app.command("uninstall")
def remove(extension_id: str) -> None:
    """Remove an installed extension."""
    if _manager().remove(extension_id):
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
def list_cmd() -> None:
    """List installed extensions."""
    entries = _manager().list()
    rows = [
        [
            e.get("id", ""),
            "enabled" if e.get("enabled", True) else "disabled",
            str(e.get("priority", "")),
        ]
        for e in entries
    ]
    print_table(["Extension", "Status", "Priority"], rows, title="Extensions")


@app.command("enable")
def enable(extension_id: str) -> None:
    """Enable an extension."""
    if _manager().set_enabled(extension_id, True):
        print_success(f"Enabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("disable")
def disable(extension_id: str) -> None:
    """Disable an extension without removing it."""
    if _manager().set_enabled(extension_id, False):
        print_success(f"Disabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("set-priority")
def set_priority(extension_id: str, value: int) -> None:
    """Set the priority of an extension (lower = higher priority in hooks)."""
    if _manager().set_priority(extension_id, value):
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
