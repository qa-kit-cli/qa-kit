"""`qakit workflow *` commands."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_table, print_warning
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.workflows.catalog import WorkflowCatalog
from qa_kit_cli.workflows.engine import WorkflowEngine

app = typer.Typer(help="Run and manage QA workflows.")
catalog_app = typer.Typer(help="Manage workflow catalogs.")
app.add_typer(catalog_app, name="catalog")


def _ctx() -> tuple[Path, Path]:
    project_root = Path.cwd()
    qakit_dir = ensure_project_layout(project_root)
    return project_root, qakit_dir


def _catalog(project_root: Path, qakit_dir: Path) -> WorkflowCatalog:
    return WorkflowCatalog(project_root, qakit_dir)


@app.command("list")
def list_cmd() -> None:
    """List available workflows."""
    project_root, qakit_dir = _ctx()
    wf_catalog = _catalog(project_root, qakit_dir)
    rows = [[w["id"], str(w["path"])] for w in wf_catalog.list()]
    print_table(["Workflow", "Path"], rows, title="Workflows")


@app.command("run")
def run(
    workflow_id: str,
    inputs: List[str] = typer.Option(
        [],
        "-i",
        help="Input key=value pairs (can repeat, e.g. -i env=staging -i scope=smoke).",
    ),
) -> None:
    """Run a workflow, optionally passing inputs."""
    project_root, qakit_dir = _ctx()

    parsed_inputs: dict[str, str] = {}
    for kv in inputs:
        if "=" in kv:
            k, v = kv.split("=", 1)
            parsed_inputs[k.strip()] = v.strip()
        else:
            print_warning(f"Ignoring malformed input '{kv}' (expected key=value).")

    engine = WorkflowEngine(project_root, qakit_dir)
    result, state = engine.run(workflow_id, parsed_inputs)
    print_info(f"Run ID: {state.run_id}")
    if not result.success:
        print_warning(f"Workflow '{workflow_id}' failed at step {state.current_step}.")
        raise typer.Exit(1)
    print_success(f"Workflow '{workflow_id}' completed (run: {state.run_id}).")


@app.command("resume")
def resume(run_id: str) -> None:
    """Resume a paused or failed workflow run."""
    project_root, qakit_dir = _ctx()
    engine = WorkflowEngine(project_root, qakit_dir)
    try:
        result, state = engine.resume(run_id)
    except FileNotFoundError:
        print_warning(f"Run '{run_id}' not found.")
        raise typer.Exit(1)
    if not result.success:
        print_warning(f"Workflow resumed but failed at step {state.current_step}.")
        raise typer.Exit(1)
    print_success(f"Workflow '{state.workflow_id}' resumed and completed (run: {run_id}).")


@app.command("status")
def status(
    run_id: Optional[str] = typer.Argument(None, help="Run ID to inspect (default: show all)."),
) -> None:
    """Show the status of a run or list all runs."""
    project_root, qakit_dir = _ctx()
    engine = WorkflowEngine(project_root, qakit_dir)

    if run_id:
        state = engine.get_run(run_id)
        if state is None:
            print_warning(f"Run '{run_id}' not found.")
            raise typer.Exit(1)
        rows = [
            ["run_id", state.run_id],
            ["workflow", state.workflow_id],
            ["status", state.status],
            ["step", str(state.current_step)],
            ["created", state.created_at],
            ["updated", state.updated_at],
        ]
        print_table(["Field", "Value"], rows, title=f"Run: {run_id}")
    else:
        runs = engine.list_runs()
        if not runs:
            print_info("No workflow runs found.")
            return
        rows_list = [[r.run_id, r.workflow_id, r.status, str(r.current_step), r.updated_at] for r in runs]
        print_table(["Run ID", "Workflow", "Status", "Step", "Updated"], rows_list, title="Workflow Runs")


@app.command("add")
def add(source: str) -> None:
    """Add a workflow from a local path or bundled ID."""
    project_root, qakit_dir = _ctx()
    src = Path(source)
    if not src.exists():
        from qa_kit_cli._assets import get_bundled_workflows_dir
        bundled = get_bundled_workflows_dir() / source
        if bundled.exists():
            src = bundled
        else:
            print_warning(f"Workflow source '{source}' not found.")
            raise typer.Exit(1)

    dst = qakit_dir / "workflows" / src.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print_success(f"Added workflow '{src.name}'.")


@app.command("remove")
def remove(workflow_id: str) -> None:
    """Remove a local workflow."""
    project_root, qakit_dir = _ctx()
    wf_dir = qakit_dir / "workflows" / workflow_id
    if not wf_dir.exists():
        print_warning(f"Workflow '{workflow_id}' is not installed locally.")
        raise typer.Exit(1)
    shutil.rmtree(wf_dir)
    print_success(f"Removed workflow '{workflow_id}'.")


@app.command("info")
def info(workflow_id: str) -> None:
    """Show details about a workflow."""
    import yaml

    project_root, qakit_dir = _ctx()
    wf_catalog = _catalog(project_root, qakit_dir)
    path = wf_catalog.get_path(workflow_id)
    if path is None:
        print_warning(f"Workflow '{workflow_id}' not found.")
        raise typer.Exit(1)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [[k, str(v)] for k, v in data.items() if k != "steps"]
    print_table(["Field", "Value"], rows, title=f"Workflow: {workflow_id}")
    steps = data.get("steps", [])
    if steps:
        step_rows = [[str(i + 1), s.get("id", ""), s.get("type", "command"), s.get("command", "")] for i, s in enumerate(steps)]
        print_table(["#", "ID", "Type", "Command"], step_rows, title="Steps")


@app.command("search")
def search(
    query: Optional[str] = typer.Argument(None),
    tag: Optional[str] = typer.Option(None, "--tag"),
) -> None:
    """Search available workflows."""
    project_root, qakit_dir = _ctx()
    wf_catalog = _catalog(project_root, qakit_dir)
    entries = wf_catalog.list()
    if query:
        entries = [e for e in entries if query.lower() in e["id"].lower()]
    rows = [[e["id"], str(e["path"])] for e in entries]
    if rows:
        print_table(["Workflow", "Path"], rows, title="Workflow Search Results")
    else:
        print_info("No workflows found matching the query.")


# --- catalog subcommands ---

@catalog_app.command("list")
def catalog_list() -> None:
    """List active workflow catalogs."""
    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "workflow-catalogs.yml"
    if not catalog_file.exists():
        print_info("No project-level workflow catalog configured (.qakit/workflow-catalogs.yml).")
        return
    import yaml
    data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs = data.get("catalogs", [])
    rows = [[c.get("name", ""), c.get("url", "")] for c in catalogs]
    print_table(["Name", "URL"], rows, title="Workflow Catalogs")


@catalog_app.command("add")
def catalog_add(
    url: str,
    name: Optional[str] = typer.Option(None, "--name"),
) -> None:
    """Add a workflow catalog URL."""
    import yaml

    project_root = Path.cwd()
    ensure_project_layout(project_root)
    catalog_file = project_root / ".qakit" / "workflow-catalogs.yml"
    data: dict = {}
    if catalog_file.exists():
        data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
    catalogs: list = data.get("catalogs", [])
    catalogs.append({"name": name or url, "url": url})
    data["catalogs"] = catalogs
    catalog_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    print_success(f"Added workflow catalog '{name or url}'.")


@catalog_app.command("remove")
def catalog_remove(name: str) -> None:
    """Remove a workflow catalog by name."""
    import yaml

    project_root = Path.cwd()
    catalog_file = project_root / ".qakit" / "workflow-catalogs.yml"
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
