"""QA Kit CLI entrypoint."""

from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

import typer

from qa_kit_cli._console import print_error, print_info, print_success, print_table
from qa_kit_cli._utils import run_command
from qa_kit_cli._version import __version__
from qa_kit_cli.commands import register_commands

_FEATURE_FLAGS: dict[str, bool] = {
    "qa_lifecycle_commands": True,
    "skills_mode": True,
    "preset_resolution": True,
    "extension_resolution": True,
    "workflow_engine": True,
    "catalog_stack": True,
    "integration_multi_install_safety": True,
    "machine_readable_version": True,
}


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


app = typer.Typer(help="QA Kit CLI - AI-assisted QA automation toolkit.")
self_app = typer.Typer(help="Self-management commands for qakit.")
app.add_typer(self_app, name="self")
register_commands(app)


@app.callback(invoke_without_command=True)
def _root_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        is_eager=True,
        callback=_version_callback,
        help="Show version and exit.",
    ),
) -> None:
    """QA Kit CLI — risk-driven QA automation: policy → strategy → test plan → tests → CI → coverage → release gate."""
    if ctx.invoked_subcommand is None and version is None:
        typer.echo(ctx.get_help())


@app.command("version")
def version_command(
    features: bool = typer.Option(False, "--features", help="Show feature flags."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON (use with --features)."),
) -> None:
    """Show CLI version and environment details."""
    if features:
        if as_json:
            payload = {
                "version": __version__,
                "python": sys.version.split()[0],
                "platform": platform.system(),
                "features": _FEATURE_FLAGS,
            }
            typer.echo(json.dumps(payload, indent=2))
        else:
            rows = [[k, "yes" if v else "no"] for k, v in _FEATURE_FLAGS.items()]
            print_table(["Feature", "Enabled"], rows, title=f"QA Kit {__version__} — Feature Flags")
        return

    rows = [
        ["qakit", __version__],
        ["python", sys.version.split()[0]],
        ["platform", platform.platform()],
        ["cwd", str(Path.cwd())],
    ]
    print_table(["Key", "Value"], rows, title="Version")


@app.command("check")
def check_command() -> None:
    """Verify local prerequisites used by QA workflows."""
    checks = ["node", "npm", "npx", "playwright", "jest", "python", "git"]
    rows: list[list[str]] = []
    missing = 0
    for tool in checks:
        resolved = shutil.which(tool)
        if resolved:
            rows.append([tool, "OK", resolved])
        else:
            missing += 1
            rows.append([tool, "MISSING", "-"])
    print_table(["Tool", "Status", "Path"], rows, title="Prerequisite Check")
    if missing:
        raise typer.Exit(1)
    print_success("All required tools were found.")


@self_app.command("update")
def self_update() -> None:
    """
    Update qakit from package index/tool manager.
    Tries uv first, then pip.
    """
    uv_cmd = ["uv", "tool", "install", "--upgrade", "qa-kit-cli"]
    rc, _, err = run_command(uv_cmd)
    if rc == 0:
        print_success("Updated qa-kit-cli with uv.")
        return

    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "qa-kit-cli"]
    rc, _, pip_err = run_command(pip_cmd)
    if rc == 0:
        print_success("Updated qa-kit-cli with pip.")
        return

    print_error("Failed to update qa-kit-cli.")
    if err.strip():
        print_info(err.strip())
    if pip_err.strip():
        print_info(pip_err.strip())
    raise typer.Exit(1)


def main() -> None:
    """Entry point for the qakit console script."""
    app()
