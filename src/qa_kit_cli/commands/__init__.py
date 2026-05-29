"""CLI command group registration."""

from __future__ import annotations

import typer

from qa_kit_cli.commands import extension, init, integration, preset, workflow


def register_commands(app: typer.Typer) -> None:
    """Attach all command groups to the root app."""
    app.command("init")(init.init_command)
    app.add_typer(integration.app, name="integration")
    app.add_typer(extension.app, name="extension")
    app.add_typer(preset.app, name="preset")
    app.add_typer(workflow.app, name="workflow")

