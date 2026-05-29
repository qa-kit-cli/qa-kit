"""`qakit preset *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
from qa_kit_cli.presets import PresetManager
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.template_resolver import TemplateResolver

app = typer.Typer(help="Manage QA Kit presets.")
catalog_app = typer.Typer(help="Manage preset catalogs.")
app.add_typer(catalog_app, name="catalog")


def _manager() -> PresetManager:
    project_root = Path.cwd()
    ensure_project_layout(project_root)
    return PresetManager(project_root)


@app.command("add")
def add(
    preset_ref: str,
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Add a preset (bundled ID, local --dev path, or --from URL)."""
    source = from_url or dev or preset_ref
    entry = _manager().add(source)
    print_success(f"Added preset '{entry['id']}'.")


@app.command("remove")
def remove(preset_id: str) -> None:
    """Remove an installed preset."""
    if _manager().remove(preset_id):
        print_success(f"Removed preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not installed.")


@app.command("list")
def list_cmd() -> None:
    """List installed presets."""
    entries = _manager().list()
    rows = [
        [
            e.get("id", ""),
            str(e.get("priority", "")),
            "enabled" if e.get("enabled", True) else "disabled",
        ]
        for e in entries
    ]
    print_table(["Preset", "Priority", "Status"], rows, title="Presets")


@app.command("priority")
@app.command("set-priority")
def priority(preset_id: str, value: int) -> None:
    """Set the priority of a preset (lower number = higher priority)."""
    if _manager().set_priority(preset_id, value):
        print_success(f"Set preset '{preset_id}' priority to {value}.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("enable")
def enable(preset_id: str) -> None:
    """Enable a preset."""
    if _manager().set_enabled(preset_id, True):
        print_success(f"Enabled preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("disable")
def disable(preset_id: str) -> None:
    """Disable a preset without removing it."""
    if _manager().set_enabled(preset_id, False):
        print_success(f"Disabled preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("search")
def search(
    query: Optional[str] = typer.Argument(None, help="Search term."),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag."),
    author: Optional[str] = typer.Option(None, "--author", help="Filter by author."),
) -> None:
    """Search available presets across active catalogs."""
    manager = _manager()
    bundled = manager.registry.list_bundled()
    rows: list[list[str]] = []
    for pid in bundled:
        if query and query.lower() not in pid.lower():
            continue
        rows.append([pid, "bundled", ""])
    if rows:
        print_table(["Preset", "Source", "Tags"], rows, title="Preset Search Results")
    else:
        print_info("No presets found matching the query.")


@app.command("info")
def info(preset_id: str) -> None:
    """Show details about an installed or bundled preset."""
    import yaml

    manager = _manager()
    try:
        src = manager.registry.resolve(preset_id)
    except FileNotFoundError:
        print_warning(f"Preset '{preset_id}' not found.")
        raise typer.Exit(1)
    manifest_file = src / "preset.yml"
    if not manifest_file.exists():
        print_warning(f"No preset.yml found in '{src}'.")
        raise typer.Exit(1)
    data = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
    rows = [[k, str(v)] for k, v in data.items() if not isinstance(v, list)]
    print_table(["Field", "Value"], rows, title=f"Preset: {preset_id}")
    comps = data.get("compositions", [])
    if comps:
        comp_rows = [[c.get("command", ""), c.get("mode", "replace")] for c in comps]
        print_table(["Command", "Mode"], comp_rows, title="Compositions")


@app.command("resolve")
def resolve(template_name: str) -> None:
    """Show the template resolution stack for a given template name.

    Example: qakit preset resolve write.playwright.md
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
    """List active preset catalogs."""
    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "preset-catalogs.yml"
    if not catalog_file.exists():
        print_info("No project-level preset catalog configured (.qakit/preset-catalogs.yml).")
        return
    import yaml
    data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs = data.get("catalogs", [])
    rows = [[c.get("name", ""), c.get("url", ""), str(c.get("priority", ""))] for c in catalogs]
    print_table(["Name", "URL", "Priority"], rows, title="Preset Catalogs")


@catalog_app.command("add")
def catalog_add(
    url: str,
    name: Optional[str] = typer.Option(None, "--name", help="Catalog name."),
    priority: int = typer.Option(50, "--priority", help="Catalog priority (lower = higher priority)."),
    install_allowed: bool = typer.Option(False, "--install-allowed", help="Allow auto-install from this catalog."),
) -> None:
    """Add a preset catalog URL."""
    import yaml

    project_root = Path.cwd()
    ensure_project_layout(project_root)
    catalog_file = project_root / ".qakit" / "preset-catalogs.yml"
    data: dict = {}
    if catalog_file.exists():
        data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs: list = data.get("catalogs", [])
    catalogs.append({"name": name or url, "url": url, "priority": priority, "install_allowed": install_allowed})
    data["catalogs"] = catalogs
    catalog_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    print_success(f"Added preset catalog '{name or url}'.")


@catalog_app.command("remove")
def catalog_remove(name: str) -> None:
    """Remove a preset catalog by name."""
    import yaml

    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "preset-catalogs.yml"
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
