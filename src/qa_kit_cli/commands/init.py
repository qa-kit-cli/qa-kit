"""`qakit init` command."""

from __future__ import annotations

from pathlib import Path

import typer

from qa_kit_cli._console import print_info, print_success
from qa_kit_cli.agents import CommandRegistrar, detect_active_integration
from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations import get_integration
from qa_kit_cli.shared_infra import ensure_memory_files, refresh_shared_infra

_CONTEXT_PREAMBLE = """\
# QA Kit

This project uses [QA Kit](https://github.com/qa-kit/qa-kit) — an AI-assisted QA automation toolkit.

## Active slash commands

All `/qakit.*` commands are installed in `.claude/commands/`. Use them to:
- `/qakit.strategy` — generate a QA strategy document
- `/qakit.testplan` — produce a structured test plan
- `/qakit.write.playwright` — write Playwright TypeScript tests
- `/qakit.write.jest` — write Jest unit/integration tests
- `/qakit.ci.github-actions` — generate CI/CD pipeline config
- `/qakit.review.pr` — QA-focused pull request review
- `/qakit.maintain.flaky` — diagnose and fix flaky tests

## Project memory

QA context files live in `.qakit/memory/`:
- `test-policy.md` — QA governance: coverage thresholds, approved frameworks, flakiness policy
- `qa-strategy.md` — risk areas and testing priorities for this project
- `test-plan.md` — live test plan with scope, environments, and exit criteria

Read these files before generating tests or CI config to ensure alignment with project standards.

## Test IDs

All test cases should be tagged with canonical IDs (`TC-001`, `TC-002`, …) as defined in `test-plan.md`.
"""


def init_command(
    integration: str | None = typer.Option(None, "--integration", "-i", help="Integration key to activate."),
) -> None:
    """Scaffold .qakit and install slash commands to the active integration."""
    project_root = Path.cwd()
    qakit_dir = refresh_shared_infra(project_root)
    ensure_memory_files(project_root)

    selected = integration or detect_active_integration(project_root)
    integration_cls = get_integration(selected)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {selected}")

    registrar = CommandRegistrar()
    installed = registrar.install_for_integration(project_root, qakit_dir, selected)

    context_path = integration_cls.get_context_file(project_root)
    if context_path and not context_path.exists():
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(_CONTEXT_PREAMBLE, encoding="utf-8")
        print_info(f"Created {context_path.relative_to(project_root)}")

    state = IntegrationState.load(qakit_dir)
    state.add(selected, {"name": integration_cls.config.get("name", selected)})
    state.set_active(selected)
    state.save(qakit_dir)

    print_success(f"Initialized QA Kit in {project_root}")
    print_info(f"Active integration: {selected}")
    print_info(f"Installed {len(installed)} command templates.")

