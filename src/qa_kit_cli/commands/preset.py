"""`qakit preset *` commands."""

from __future__ import annotations

from pathlib import Path

import typer

from qa_kit_cli._console import print_success, print_table, print_warning
from qa_kit_cli.presets import PresetManager
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage QA Kit presets.")


def _manager() -> PresetManager:
    project_root = Path.cwd()
    ensure_project_layout(project_root)
    return PresetManager(project_root)


@app.command("add")
def add(preset_ref: str) -> None:
    entry = _manager().add(preset_ref)
    print_success(f"Added preset '{entry['id']}'.")


@app.command("remove")
def remove(preset_id: str) -> None:
    if _manager().remove(preset_id):
        print_success(f"Removed preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not installed.")


@app.command("list")
def list_cmd() -> None:
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
def priority(preset_id: str, value: int) -> None:
    if _manager().set_priority(preset_id, value):
        print_success(f"Set preset '{preset_id}' priority to {value}.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("enable")
def enable(preset_id: str) -> None:
    if _manager().set_enabled(preset_id, True):
        print_success(f"Enabled preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")


@app.command("disable")
def disable(preset_id: str) -> None:
    if _manager().set_enabled(preset_id, False):
        print_success(f"Disabled preset '{preset_id}'.")
        return
    print_warning(f"Preset '{preset_id}' was not found.")

