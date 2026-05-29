"""`qakit init` command."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, List, Optional

import typer

from qa_kit_cli._console import print_info, print_success, print_warning
from qa_kit_cli._integration_options import parse_integration_options
from qa_kit_cli.agents import CommandRegistrar, SkillRegistrar, detect_active_integration
from qa_kit_cli.integration_state import IntegrationState
from qa_kit_cli.integrations import get_integration
from qa_kit_cli.presets import PresetManager
from qa_kit_cli.project_config import ProjectConfig
from qa_kit_cli.shared_infra import ensure_memory_files, refresh_shared_infra

_CONTEXT_PREAMBLE = """\
# QA Kit

This project uses [QA Kit](https://github.com/qa-kit-cli/qa-kit) — an AI-assisted QA automation toolkit.

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

_CLI_MAP: dict[str, list[str]] = {
    "claude": ["claude"],
    "codex": ["codex"],
    "copilot": ["gh"],
    "gemini": ["gemini"],
    "cursor": ["cursor"],
    "windsurf": ["windsurf"],
    "amp": ["amp"],
    "opencode": ["opencode"],
    "goose": ["goose"],
}


def _is_empty(path: Path) -> bool:
    return not any(path.iterdir())


def init_command(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Directory to initialize. Omit or use '.' for the current directory.",
    ),
    here: bool = typer.Option(False, "--here", help="Initialize the current directory."),
    force: bool = typer.Option(
        False, "--force", help="Allow initialization in a non-empty directory."
    ),
    integration: Optional[str] = typer.Option(
        None, "--integration", "-i", help="Integration key to activate."
    ),
    integration_options: Optional[str] = typer.Option(
        None,
        "--integration-options",
        help="Agent-specific options, e.g. '--skills --commands-dir .myagent/cmds'.",
    ),
    preset: List[str] = typer.Option(
        [],
        "--preset",
        help="Install preset(s) before registering commands (can repeat).",
    ),
    ignore_agent_tools: bool = typer.Option(
        False, "--ignore-agent-tools", help="Skip checking whether agent CLIs exist."
    ),
    script: str = typer.Option(
        "ps", "--script", help="Platform script type: 'sh' (bash) or 'ps' (PowerShell)."
    ),
) -> None:
    """Scaffold .qakit and install slash commands to the active integration."""
    # 1. Resolve target directory
    if project_name and project_name != "." and not here:
        project_root = Path.cwd() / project_name
        if project_root.exists() and not project_root.is_dir():
            raise typer.BadParameter(f"'{project_name}' exists and is not a directory.")
        if project_root.exists() and not _is_empty(project_root) and not force:
            raise typer.BadParameter(
                f"Directory '{project_name}' is not empty. Use --force to initialize anyway."
            )
        project_root.mkdir(parents=True, exist_ok=True)
    else:
        project_root = Path.cwd()

    # 2. Parse integration options
    int_opts: dict[str, Any] = parse_integration_options(integration_options)
    skills_mode = bool(int_opts.get("skills", False))

    # 3. Scaffold .qakit and copy bundled assets
    qakit_dir = refresh_shared_infra(project_root)
    ensure_memory_files(project_root)

    # 4. Install presets first so their overrides apply to command rendering
    if preset:
        manager = PresetManager(project_root)
        for p in preset:
            try:
                manager.add(p)
                print_info(f"Installed preset '{p}'.")
            except FileNotFoundError:
                print_warning(f"Preset '{p}' not found — skipping.")

    # 5. Resolve integration
    selected = integration or detect_active_integration(project_root)
    integration_cls = get_integration(selected)
    if integration_cls is None:
        raise typer.BadParameter(f"Unknown integration: {selected}")

    # 6. Optionally verify agent CLI is installed
    if not ignore_agent_tools and integration_cls.config.get("requires_cli"):
        cli_names = _CLI_MAP.get(selected, [])
        if cli_names and not any(shutil.which(c) for c in cli_names):
            install_url = integration_cls.config.get("install_url", "")
            print_warning(
                f"Agent CLI for '{selected}' not found on PATH. "
                f"Install it from: {install_url}\n"
                "  Pass --ignore-agent-tools to suppress this warning."
            )

    # 7. Install commands or skills
    if skills_mode and integration_cls.supports_skills:
        skill_reg = SkillRegistrar()
        installed = skill_reg.install_for_integration(project_root, qakit_dir, selected)
        mode_label = "skills"
    else:
        cmd_reg = CommandRegistrar()
        installed = cmd_reg.install_for_integration(project_root, qakit_dir, selected)
        mode_label = "commands"

    # 8. Write context file
    context_path = integration_cls.get_context_file(project_root)
    if context_path and not context_path.exists():
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(_CONTEXT_PREAMBLE, encoding="utf-8")
        print_info(f"Created {context_path.relative_to(project_root)}")

    # 9. Persist integration state
    state = IntegrationState.load(qakit_dir)
    meta: dict[str, Any] = {
        "name": integration_cls.config.get("name", selected),
        "mode": "skills" if skills_mode and integration_cls.supports_skills else "commands",
    }
    if int_opts:
        meta["options"] = int_opts
    state.add(selected, meta)
    state.set_active(selected)
    state.save(qakit_dir)

    # 10. Persist project config
    cfg = ProjectConfig.load(qakit_dir)
    if script in ("sh", "ps"):
        cfg.script = script
    cfg.save(qakit_dir)

    print_success(f"Initialized QA Kit in {project_root}")
    print_info(f"Active integration: {selected} (mode: {mode_label})")
    print_info(f"Installed {len(installed)} {mode_label}.")
