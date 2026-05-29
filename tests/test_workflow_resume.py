"""Tests for workflow run state persistence and resume."""

from __future__ import annotations

from pathlib import Path

import pytest

from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.workflows.engine import WorkflowEngine
from qa_kit_cli.workflows.run_state import RunState, list_runs


def test_run_state_persisted_after_workflow(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("qakit")
    runs_dir = qakit_dir / "workflows" / "runs"
    assert (runs_dir / state.run_id / "state.json").exists()


def test_run_state_has_correct_workflow_id(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("qakit")
    assert state.workflow_id == "qakit"


def test_run_state_status_is_completed_on_success(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("qakit")
    assert state.status == "completed"


def test_run_state_status_is_failed_on_failure(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    wf_dir = qakit_dir / "workflows" / "fail-wf"
    wf_dir.mkdir(parents=True)
    (wf_dir / "workflow.yml").write_text(
        "id: fail-wf\nsteps:\n  - id: fail\n    type: shell\n    run: 'exit 1'\n",
        encoding="utf-8",
    )
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("fail-wf")
    assert state.status == "failed"


def test_list_runs_returns_completed_run(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("qakit")
    runs = engine.list_runs()
    run_ids = [r.run_id for r in runs]
    assert state.run_id in run_ids


def test_get_run_returns_state(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("qakit")
    fetched = engine.get_run(state.run_id)
    assert fetched is not None
    assert fetched.run_id == state.run_id


def test_get_run_returns_none_for_unknown_id(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    assert engine.get_run("nonexistent-run-id") is None


def test_resume_completed_run_returns_success(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    _, state = engine.run("qakit")
    result, resumed_state = engine.resume(state.run_id)
    assert result.success


def test_resume_unknown_run_raises(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    with pytest.raises(FileNotFoundError):
        engine.resume("no-such-run-id")


def test_run_state_inputs_preserved(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    inputs = {"env": "staging", "scope": "smoke"}
    _, state = engine.run("qakit", inputs=inputs)
    fetched = engine.get_run(state.run_id)
    assert fetched is not None
    assert fetched.inputs == inputs


def test_run_state_new_creates_unique_ids(project_dir) -> None:
    state1 = RunState.new("wf", {})
    state2 = RunState.new("wf", {})
    assert state1.run_id != state2.run_id
