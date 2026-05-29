from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.workflows.base import StepContext, StepResult
from qa_kit_cli.workflows.catalog import WorkflowCatalog
from qa_kit_cli.workflows.engine import WorkflowEngine, _command_to_hook_prefix
from qa_kit_cli.workflows.expressions import resolve_expressions
from qa_kit_cli.workflows.steps import CommandStep, GateStep, ParallelStep, ShellStep


# ---------------------------------------------------------------------------
# _command_to_hook_prefix
# ---------------------------------------------------------------------------


def test_command_to_hook_prefix_maps_correctly() -> None:
    assert _command_to_hook_prefix("qakit.strategy") == "strategy"
    assert _command_to_hook_prefix("qakit.write.playwright") == "write_playwright"
    assert _command_to_hook_prefix("qakit.ci.github-actions") == "ci_github_actions"
    assert _command_to_hook_prefix("qakit.review.bugreport") == "review_bugreport"
    assert _command_to_hook_prefix("qakit.maintain.flaky") == "maintain_flaky"


def test_command_to_hook_prefix_returns_none_for_non_qakit() -> None:
    assert _command_to_hook_prefix("other.command") is None
    assert _command_to_hook_prefix("") is None
    assert _command_to_hook_prefix("qakit") is None  # no suffix


# ---------------------------------------------------------------------------
# resolve_expressions
# ---------------------------------------------------------------------------


def test_resolve_expressions_substitutes_simple_input() -> None:
    result = resolve_expressions("Hello {{ inputs.name }}", {"name": "World"})
    assert result == "Hello World"


def test_resolve_expressions_substitutes_multiple_placeholders() -> None:
    result = resolve_expressions("{{ inputs.a }} and {{ inputs.b }}", {"a": "foo", "b": "bar"})
    assert result == "foo and bar"


def test_resolve_expressions_returns_empty_for_unknown_key() -> None:
    result = resolve_expressions("{{ inputs.unknown }}", {})
    assert result == ""


def test_resolve_expressions_works_on_nested_dict() -> None:
    step = {"command": "{{ inputs.cmd }}", "description": "run {{ inputs.cmd }}"}
    resolved = resolve_expressions(step, {"cmd": "qakit.strategy"})
    assert resolved["command"] == "qakit.strategy"
    assert resolved["description"] == "run qakit.strategy"


def test_resolve_expressions_works_on_list() -> None:
    items = ["{{ inputs.x }}", "static"]
    result = resolve_expressions(items, {"x": "dynamic"})
    assert result == ["dynamic", "static"]


def test_resolve_expressions_passes_through_non_string_values() -> None:
    assert resolve_expressions(42, {}) == 42
    assert resolve_expressions(None, {}) is None
    assert resolve_expressions(True, {}) is True


# ---------------------------------------------------------------------------
# WorkflowCatalog
# ---------------------------------------------------------------------------


def test_workflow_catalog_lists_bundled_qakit_workflow(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    catalog = WorkflowCatalog(project_dir, qakit_dir)
    entries = catalog.list()
    ids = [e["id"] for e in entries]
    assert "qakit" in ids


def test_workflow_catalog_get_path_returns_path_for_qakit(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    catalog = WorkflowCatalog(project_dir, qakit_dir)
    path = catalog.get_path("qakit")
    assert path is not None
    assert path.exists()


def test_workflow_catalog_get_path_returns_none_for_unknown(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    catalog = WorkflowCatalog(project_dir, qakit_dir)
    assert catalog.get_path("not-a-real-workflow-id") is None


def test_workflow_catalog_local_workflow_takes_precedence(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    local_wf_dir = qakit_dir / "workflows" / "qakit"
    local_wf_dir.mkdir(parents=True)
    (local_wf_dir / "workflow.yml").write_text(
        "id: qakit\nsteps: []\n", encoding="utf-8"
    )
    catalog = WorkflowCatalog(project_dir, qakit_dir)
    path = catalog.get_path("qakit")
    assert path is not None
    assert str(local_wf_dir) in str(path)


# ---------------------------------------------------------------------------
# WorkflowEngine — run
# ---------------------------------------------------------------------------


def test_workflow_engine_runs_bundled_workflow(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("qakit")
    assert result.success
    assert state.status == "completed"


def test_workflow_engine_fails_on_unknown_workflow(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    import pytest as _pytest
    with _pytest.raises(FileNotFoundError):
        engine.run("not-a-real-workflow")


def test_workflow_engine_persists_run_state(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("qakit")
    assert state.run_id
    run_dir = qakit_dir / "workflows" / "runs" / state.run_id
    assert run_dir.exists()
    assert (run_dir / "state.json").exists()


def test_workflow_engine_logs_dispatched_commands(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    engine.run("qakit")
    log = qakit_dir / "workflow-runs" / "commands.log"
    # commands.log is written by CommandStep, not the engine run-state
    assert log.exists()
    content = log.read_text(encoding="utf-8")
    assert "qakit.strategy" in content


# ---------------------------------------------------------------------------
# Hooks fire / don't fire
# ---------------------------------------------------------------------------


def test_hooks_fire_for_command_step(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)

    mock_execute = MagicMock(return_value=[])
    engine._hook_executor.execute = mock_execute  # type: ignore[method-assign]
    fake_manifest = MagicMock()
    fake_manifest.hooks = ["before_strategy", "after_strategy"]
    engine._active_manifests = [fake_manifest]

    result, state = engine.run("qakit")
    assert result.success

    calls = [call.args for call in mock_execute.call_args_list]
    events = [c[1] for c in calls]
    assert "before_strategy" in events
    assert "after_strategy" in events


def test_hooks_do_not_fire_for_failed_step(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)

    wf_dir = qakit_dir / "workflows" / "fail-test"
    wf_dir.mkdir(parents=True)
    (wf_dir / "workflow.yml").write_text(
        "id: fail-test\nsteps:\n  - id: boom\n    type: shell\n    run: 'exit 1'\n"
        "  - id: cmd\n    type: command\n    command: qakit.strategy\n",
        encoding="utf-8",
    )

    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    mock_execute = MagicMock(return_value=[])
    engine._hook_executor.execute = mock_execute  # type: ignore[method-assign]

    result, state = engine.run("fail-test")
    assert not result.success
    events = [call.args[1] for call in mock_execute.call_args_list]
    assert "before_strategy" not in events


# ---------------------------------------------------------------------------
# Step types
# ---------------------------------------------------------------------------


def test_gate_step_passes_in_non_interactive_mode(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir, non_interactive=True)
    step_data = {"type": "gate", "prompt": "Continue?", "default": True}
    result = GateStep().run(step_data, ctx)
    assert result.success


def test_gate_step_rejects_in_non_interactive_mode_when_default_false(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir, non_interactive=True)
    step_data = {"type": "gate", "prompt": "Confirm?", "default": False}
    result = GateStep().run(step_data, ctx)
    assert not result.success


def test_command_step_logs_to_commands_log(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir)
    step_data = {"type": "command", "command": "qakit.strategy"}
    result = CommandStep().run(step_data, ctx)
    assert result.success
    log = qakit_dir / "workflow-runs" / "commands.log"
    assert log.exists()
    assert "qakit.strategy" in log.read_text(encoding="utf-8")


def test_command_step_fails_when_command_missing(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir)
    result = CommandStep().run({"type": "command", "command": ""}, ctx)
    assert not result.success


def test_parallel_step_requires_non_empty_steps(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir, non_interactive=True)
    result = ParallelStep().run({"type": "parallel", "steps": []}, ctx)
    assert not result.success


def test_parallel_step_runs_multiple_command_substeps(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    ctx = StepContext(project_dir, qakit_dir, non_interactive=True)
    substeps = [
        {"type": "command", "command": "qakit.strategy"},
        {"type": "command", "command": "qakit.testplan"},
        {"type": "command", "command": "qakit.coverage"},
    ]
    result = ParallelStep().run({"type": "parallel", "steps": substeps}, ctx)
    assert result.success
    # Parallel command steps each return a "Dispatched …" output; all three must succeed
    assert result.output.count("Dispatched") == 3
