"""`qakit suite *` commands — manage per-feature QA suite directories."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import box
from rich.table import Table

from qa_kit_cli._console import console, print_info, print_success, print_warning
from qa_kit_cli.project_config import ProjectConfig
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.suite_config import (
    SUITE_MEMORY_FILES,
    SuiteIndex,
    create_suite,
    get_active_suite,
    list_suites,
)

app = typer.Typer(help="Manage per-feature QA suite directories.")


def _ctx() -> tuple[Path, Path]:
    """Return (project_root, qakit_dir) for the current working directory."""
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    return project_root, qakit_dir


@app.command("list")
def list_cmd() -> None:
    """List all suites with ID, name, path, and file counts."""
    project_root, qakit_dir = _ctx()
    cfg = ProjectConfig.load(qakit_dir)
    suites = list_suites(qakit_dir)

    table = Table(title="QA Suites", show_header=True, header_style="bold cyan", box=box.SIMPLE)
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Files")

    for s in suites:
        suite_path = project_root / s.path
        file_count = sum(1 for f in SUITE_MEMORY_FILES if (suite_path / f).exists())
        marker = "● " if s.id == cfg.active_suite else "  "
        table.add_row(f"{marker}{s.id}", s.name, s.path, str(file_count))

    console.print(table)
    if not suites:
        print_info("No suites found. Create one with: qakit suite create <name>")


@app.command("create")
def create(name: str) -> None:
    """Create a new suite under .qakit/suites/."""
    project_root, qakit_dir = _ctx()
    cfg = ProjectConfig.load(qakit_dir)
    entry = create_suite(qakit_dir=qakit_dir, name=name, branch_numbering=cfg.branch_numbering)
    print_success(
        f"Suite [bold]{entry.id}[/bold] created at "
        f"{(project_root / entry.path).relative_to(Path.cwd())}"
    )


@app.command("switch")
def switch(suite_id: str) -> None:
    """Set the active suite in config.json."""
    project_root, qakit_dir = _ctx()
    index = SuiteIndex.load(qakit_dir)
    entry = index.get(suite_id)
    if entry is None:
        print_warning(f"Suite '{suite_id}' not found. Run 'qakit suite list' to see available suites.")
        raise typer.Exit(1)
    cfg = ProjectConfig.load(qakit_dir)
    cfg.active_suite = suite_id
    cfg.save(qakit_dir)
    print_success(f"Active suite set to [bold]{suite_id}[/bold].")


@app.command("info")
def info(
    suite_id: str | None = typer.Argument(None, help="Suite ID (default: active suite)."),
) -> None:
    """Show details for a suite or the currently active suite."""
    project_root, qakit_dir = _ctx()

    if suite_id is None:
        entry = get_active_suite(qakit_dir)
        if entry is None:
            print_warning("No active suite. Pass a suite ID or run 'qakit suite switch <id>'.")
            raise typer.Exit(1)
    else:
        index = SuiteIndex.load(qakit_dir)
        entry = index.get(suite_id)
        if entry is None:
            print_warning(f"Suite '{suite_id}' not found.")
            raise typer.Exit(1)

    suite_path = project_root / entry.path
    table = Table(
        title=f"Suite: {entry.id}",
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE,
    )
    table.add_column("File")
    table.add_column("Status")

    description = ""
    for filename in SUITE_MEMORY_FILES:
        fp = suite_path / filename
        exists = fp.exists()
        status = "OK" if exists else "missing"
        if exists and filename == "test-plan.md" and not description:
            for line in fp.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    description = stripped[:80]
                    break
        table.add_row(filename, status)

    console.print(f"\n[bold]ID:[/bold]   {entry.id}")
    console.print(f"[bold]Name:[/bold] {entry.name}")
    console.print(f"[bold]Path:[/bold] {entry.path}")
    if description:
        console.print(f"[bold]Plan:[/bold] {description}")
    console.print()
    console.print(table)
