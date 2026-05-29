"""QA Kit CLI entrypoint."""

from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from packaging.version import InvalidVersion, Version

from qa_kit_cli._console import console, print_error, print_info, print_success, print_table, print_warning
from qa_kit_cli._github_http import safe_fetch_json
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


@app.command("self-check")
def self_check_cmd(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Machine-readable JSON output for CI."),
    ] = False,
) -> None:
    """Check whether the installed qakit CLI is up to date with PyPI."""
    payload = safe_fetch_json("https://pypi.org/pypi/qa-kit-cli/json", {})
    latest: str | None = None
    if isinstance(payload, dict):
        info = payload.get("info", {})
        if isinstance(info, dict):
            latest = str(info.get("version", "")).strip() or None

    up_to_date: bool | None = None
    if latest:
        try:
            up_to_date = not (Version(latest) > Version(__version__))
        except InvalidVersion:
            up_to_date = None

    if json_output:
        typer.echo(json.dumps({"installed": __version__, "latest": latest or "unknown", "up_to_date": bool(up_to_date)}))
        if up_to_date is False:
            raise typer.Exit(1)
        return

    if latest is None:
        print_warning("Could not fetch latest version from PyPI — check your network connection.")
        raise typer.Exit(1)
    if up_to_date is False:
        print_warning(f"Update available: {__version__} → {latest}. Run 'qakit self update'.")
        raise typer.Exit(1)
    if up_to_date is None:
        print_warning(f"Unable to compare versions (installed={__version__}, latest={latest}).")
        raise typer.Exit(1)
    print_success(f"qakit is up to date ({__version__}).")


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


@self_app.command("check")
def self_check() -> None:
    """Show installed version, update status, runtime details, and feature flags."""
    print_info(f"qa-kit-cli {__version__}")

    latest_version: str | None = None
    payload = safe_fetch_json("https://pypi.org/pypi/qa-kit-cli/json", None)
    if isinstance(payload, dict):
        info = payload.get("info", {})
        if isinstance(info, dict):
            latest_version = str(info.get("version", "")).strip() or None

    if latest_version:
        try:
            current_v = Version(__version__)
            latest_v = Version(latest_version)
            if latest_v > current_v:
                console.print(
                    f"[yellow]⚠ Update available: {__version__} → {latest_version}. "
                    "Run `qakit self update` to upgrade.[/yellow]"
                )
            else:
                console.print(f"[green]✓ qa-kit-cli is up to date ({__version__})[/green]")
        except InvalidVersion:
            print_warning(f"Unable to compare versions (installed={__version__}, latest={latest_version}).")
    else:
        print_warning("Could not fetch latest version from PyPI.")

    env_rows = [
        ["python", sys.version.split()[0]],
        ["platform", platform.platform()],
    ]
    print_table(["Key", "Value"], env_rows, title="Runtime")

    feature_rows = [[k, "yes" if v else "no"] for k, v in _FEATURE_FLAGS.items()]
    print_table(["Feature", "Enabled"], feature_rows, title="Feature Flags")


def main() -> None:
    """Entry point for the qakit console script."""
    app()
