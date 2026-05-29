"""`qakit extension *` commands."""

from __future__ import annotations

from pathlib import Path

import typer

from qa_kit_cli._console import print_success, print_table, print_warning
from qa_kit_cli.extensions import ExtensionManager
from qa_kit_cli.shared_infra import ensure_project_layout

app = typer.Typer(help="Manage QA Kit extensions.")


def _manager() -> ExtensionManager:
    project_root = Path.cwd()
    ensure_project_layout(project_root)
    return ExtensionManager(project_root)


@app.command("add")
def add(extension_ref: str) -> None:
    entry = _manager().add(extension_ref)
    print_success(f"Added extension '{entry['id']}'.")


@app.command("remove")
def remove(extension_id: str) -> None:
    if _manager().remove(extension_id):
        print_success(f"Removed extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not installed.")


@app.command("list")
def list_cmd() -> None:
    entries = _manager().list()
    rows = [[e.get("id", ""), "enabled" if e.get("enabled", True) else "disabled"] for e in entries]
    print_table(["Extension", "Status"], rows, title="Extensions")


@app.command("enable")
def enable(extension_id: str) -> None:
    if _manager().set_enabled(extension_id, True):
        print_success(f"Enabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")


@app.command("disable")
def disable(extension_id: str) -> None:
    if _manager().set_enabled(extension_id, False):
        print_success(f"Disabled extension '{extension_id}'.")
        return
    print_warning(f"Extension '{extension_id}' was not found.")

