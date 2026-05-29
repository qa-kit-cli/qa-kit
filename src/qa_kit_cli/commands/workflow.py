"""`qakit workflow *` commands."""

from __future__ import annotations

from pathlib import Path

import typer

from qa_kit_cli._console import print_success, print_table
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.workflows.catalog import WorkflowCatalog
from qa_kit_cli.workflows.engine import WorkflowEngine

app = typer.Typer(help="Run and list QA workflows.")


def _catalog(project_root: Path) -> WorkflowCatalog:
    qakit_dir = ensure_project_layout(project_root)
    return WorkflowCatalog(project_root, qakit_dir)


@app.command("list")
def list_cmd() -> None:
    catalog = _catalog(Path.cwd())
    rows = [[w["id"], str(w["path"])] for w in catalog.list()]
    print_table(["Workflow", "Path"], rows, title="Workflows")


@app.command("run")
def run(workflow_id: str) -> None:
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    engine = WorkflowEngine(project_root, qakit_dir)
    result = engine.run(workflow_id)
    if not result.success:
        raise typer.Exit(1)
    print_success(f"Workflow '{workflow_id}' completed.")

