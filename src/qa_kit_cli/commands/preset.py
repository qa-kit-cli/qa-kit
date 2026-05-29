"""`qakit preset *` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel

from qa_kit_cli._console import console, print_info, print_success, print_table, print_warning
from qa_kit_cli.catalogs import PresetCatalogStack
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


def _reregister_active(project_root: Path, qakit_dir: Path) -> None:
    """Reinstall commands for the active integration so preset templates apply."""
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


_preset_alias_shown: set[str] = set()


def _do_add_preset(
    preset_ref: str,
    priority: int,
    dev: Optional[str],
    from_url: Optional[str],
) -> None:
    """Shared implementation for install and add preset commands."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    source = from_url or dev or preset_ref
    manager = PresetManager(project_root)
    entry = manager.add(source, priority=priority)
    _reregister_active(project_root, qakit_dir)
    print_success(f"Added preset '{entry['id']}' (priority={priority}).")


def _do_remove_preset(preset_id: str) -> None:
    """Shared implementation for uninstall and remove preset commands."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if PresetManager(project_root).remove(preset_id):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Removed preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not installed.")


@app.command("install")
def install_preset(
    preset_ref: str,
    priority: int = typer.Option(10, "--priority", help="Preset priority (lower = higher priority). Default: 10."),
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Install a preset (bundled ID, local --dev path, or --from URL)."""
    _do_add_preset(preset_ref, priority, dev, from_url)


@app.command("add")
def add(
    preset_ref: str,
    priority: int = typer.Option(10, "--priority", help="Preset priority (lower = higher priority). Default: 10."),
    dev: Optional[str] = typer.Option(None, "--dev", help="Install from a local directory path."),
    from_url: Optional[str] = typer.Option(None, "--from", help="Install from a URL."),
) -> None:
    """Alias for install."""
    if "preset.add" not in _preset_alias_shown:
        _preset_alias_shown.add("preset.add")
        print_info(
            "Tip: 'qakit preset add' is an alias for 'qakit preset install'.\n"
            "     Both work identically — 'install' is the preferred name going forward."
        )
    _do_add_preset(preset_ref, priority, dev, from_url)


@app.command("uninstall")
def uninstall_preset(preset_id: str) -> None:
    """Remove an installed preset."""
    _do_remove_preset(preset_id)


@app.command("remove")
def remove(preset_id: str) -> None:
    """Alias for uninstall."""
    if "preset.remove" not in _preset_alias_shown:
        _preset_alias_shown.add("preset.remove")
        print_info(
            "Tip: 'qakit preset remove' is an alias for 'qakit preset uninstall'.\n"
            "     Both work identically — 'uninstall' is the preferred name going forward."
        )
    _do_remove_preset(preset_id)


@app.command("list")
def list_cmd() -> None:
    """List installed presets with id, name, version, priority, status, template count, description."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    manager = PresetManager(project_root)
    entries = manager.list()
    rows: list[list[str]] = []
    for e in entries:
        preset_id = str(e.get("id", ""))
        name = version_str = description = template_count = ""
        preset_path = qakit_dir / "presets" / preset_id
        manifest_file = preset_path / "preset.yml"
        if manifest_file.exists():
            try:
                import yaml as _yaml
                d = _yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
                name = str(d.get("name", preset_id))
                version_str = str(d.get("version", ""))
                description = str(d.get("description", ""))
                tmpl_dir = preset_path / "templates" / "commands"
                template_count = str(len(list(tmpl_dir.glob("*.md")))) if tmpl_dir.exists() else "0"
            except Exception:
                pass
        rows.append([
            preset_id,
            name,
            version_str,
            str(e.get("priority", 10)),
            "enabled" if e.get("enabled", True) else "disabled",
            template_count,
            description[:60],
        ])
    print_table(["ID", "Name", "Version", "Priority", "Status", "Templates", "Description"], rows, title="Installed Presets")


@app.command("priority")
@app.command("set-priority")
def priority(preset_id: str, value: int) -> None:
    """Set the priority of a preset (lower number = higher priority)."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if PresetManager(project_root).set_priority(preset_id, value):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Set preset '{preset_id}' priority to {value}.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("enable")
def enable(preset_id: str) -> None:
    """Enable a preset."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if PresetManager(project_root).set_enabled(preset_id, True):
        _reregister_active(project_root, qakit_dir)
        print_success(f"Enabled preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("disable")
def disable(preset_id: str) -> None:
    """Disable a preset without removing it."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    if PresetManager(project_root).set_enabled(preset_id, False):
        _reregister_active(project_root, qakit_dir)
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
    stack = PresetCatalogStack(Path.cwd(), include_community=True)
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
        pid = str(item.get("id", ""))
        rows.append(
            [
                pid,
                str(item.get("name", "")),
                str(item.get("version", "")),
                str(item.get("description", "")),
                "Yes" if pid in installed_ids else "No",
            ]
        )
    if rows:
        print_table(["ID", "Name", "Version", "Description", "Installed"], rows, title="Preset Search Results")
    else:
        print_info("No presets found matching the query.")


@app.command("info")
def info(preset_id: str) -> None:
    """Show details about an installed or bundled preset."""
    import yaml

    manager = _manager()
    stack = PresetCatalogStack(Path.cwd(), include_community=True)
    catalog_entry = stack.get(preset_id)
    installed_entry = next((e for e in manager.list() if str(e.get("id", "")) == preset_id), None)

    data: dict = {}
    source_label = "catalog"
    source_ref = str(catalog_entry.get("_source_ref", "")) if catalog_entry else ""
    manifest_path: Path | None = None

    if installed_entry:
        manifest_path = Path.cwd() / ".qakit" / "presets" / preset_id / "preset.yml"
    else:
        try:
            src = manager.registry.resolve(preset_id)
            manifest_path = src / "preset.yml"
            if "presets" in str(src):
                source_label = "bundled"
                source_ref = "bundled"
        except FileNotFoundError:
            manifest_path = None

    if manifest_path and manifest_path.exists():
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    elif catalog_entry:
        data = dict(catalog_entry)
    else:
        print_warning(f"Preset '{preset_id}' not found.")
        raise typer.Exit(1)

    compositions = data.get("compositions", [])
    command_list = [str(c.get("command", "")) for c in compositions] if isinstance(compositions, list) else []
    hooks = data.get("hooks", [])
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
        f"Name:        {data.get('name', preset_id)}\n"
        f"ID:          {data.get('id', preset_id)}\n"
        f"Version:     {data.get('version', '')}\n"
        f"Author:      {data.get('author', '')}\n"
        f"Description: {data.get('description', '')}\n"
        f"Hooks:       {', '.join(str(h) for h in hooks) if hooks else '-'}\n"
        f"Commands:    {', '.join(command_list) if command_list else '-'}\n"
        f"Installed:   {'Yes' if installed_entry else 'No'}\n"
        f"Source:      {source_display}"
    )
    console.print(Panel(panel_text, title=f"Preset: {preset_id}", border_style="cyan"))


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
