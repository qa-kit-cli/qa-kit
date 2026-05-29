"""QA Kit CLI entrypoint."""

from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

import typer

from qa_kit_cli._console import print_error, print_info, print_success, print_table
from qa_kit_cli._utils import run_command
from qa_kit_cli._version import __version__
from qa_kit_cli.commands import register_commands

app = typer.Typer(help="QA Kit CLI - AI-assisted QA automation toolkit.")
self_app = typer.Typer(help="Self-management commands for qakit.")
app.add_typer(self_app, name="self")
register_commands(app)


@app.command("version")
def version_command() -> None:
    """Show CLI version and environment details."""
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
