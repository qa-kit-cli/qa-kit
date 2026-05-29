"""Tests for workflow engine improvements: gate pause/resume, input schema, unsupported steps."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.workflows.engine import WorkflowEngine
from qa_kit_cli.workflows.input_schema import validate_and_apply
from qa_kit_cli.workflows.steps.gate_step import GateStep
from qa_kit_cli.workflows.base import StepContext, StepResult
from qa_kit_cli.workflows.steps.unsupported_step import (
    DoWhileStep,
    FanInStep,
    FanOutStep,
    PromptStep,
    SwitchStep,
    WhileStep,
)


def _make_workflow(qakit_dir: Path, wf_id: str, content: str) -> None:
    """Write a workflow so WorkflowCatalog finds it via rglob('workflow.yml')."""
    wf_dir = qakit_dir / "workflows" / wf_id
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "workflow.yml").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Gate step: proper pause signal
# ---------------------------------------------------------------------------

def test_gate_approved_returns_success(qakit_dir: Path) -> None:
    ctx = StepContext(qakit_dir.parent, qakit_dir, inputs={}, non_interactive=True)
    result = GateStep().run({"type": "gate", "default": True}, ctx)
    assert result.success is True
    assert result.paused is False


def test_gate_rejected_sets_paused_flag(qakit_dir: Path) -> None:
    ctx = StepContext(qakit_dir.parent, qakit_dir, inputs={}, non_interactive=True)
    result = GateStep().run({"type": "gate", "default": False}, ctx)
    assert result.success is False
    assert result.paused is True


def test_gate_pause_sets_workflow_status_paused(project_dir: Path) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    wf = textwrap.dedent("""\
        id: gate-test
        steps:
          - type: gate
            default: false
    """)
    _make_workflow(qakit_dir, "gate-test", wf)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("gate-test")
    assert result.paused is True
    assert state.status == "paused"


def test_gate_pause_can_be_resumed(project_dir: Path) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    # Two-step workflow: gate (default=True) then shell
    wf = textwrap.dedent("""\
        id: gate-resume
        steps:
          - type: gate
            default: true
          - type: shell
            command: echo done
    """)
    _make_workflow(qakit_dir, "gate-resume", wf)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("gate-resume")
    assert state.status == "completed"
    assert result.success is True


# ---------------------------------------------------------------------------
# Unsupported step types return informative error
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("step_cls,step_type", [
    (PromptStep, "prompt"),
    (SwitchStep, "switch"),
    (WhileStep, "while"),
    (DoWhileStep, "do-while"),
    (FanOutStep, "fan-out"),
    (FanInStep, "fan-in"),
])
def test_unsupported_step_returns_failure(step_cls, step_type, qakit_dir: Path) -> None:
    ctx = StepContext(qakit_dir.parent, qakit_dir, inputs={}, non_interactive=True)
    result = step_cls().run({"type": step_type}, ctx)
    assert result.success is False
    assert step_type in result.output


def test_unsupported_step_type_in_workflow(project_dir: Path) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    wf = textwrap.dedent("""\
        id: unsupported-test
        steps:
          - type: while
            condition: "{{ inputs.count > 0 }}"
    """)
    _make_workflow(qakit_dir, "unsupported-test", wf)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("unsupported-test")
    assert result.success is False
    assert state.status == "failed"


# ---------------------------------------------------------------------------
# Input schema validation
# ---------------------------------------------------------------------------

def test_validate_applies_string_default() -> None:
    schema = [{"name": "env", "type": "string", "default": "staging"}]
    result = validate_and_apply({}, schema)
    assert result["env"] == "staging"


def test_validate_required_missing_raises() -> None:
    schema = [{"name": "feature", "type": "string", "required": True}]
    with pytest.raises(ValueError, match="Required input 'feature' is missing"):
        validate_and_apply({}, schema)


def test_validate_boolean_coercion() -> None:
    schema = [{"name": "flag", "type": "boolean", "default": False}]
    result = validate_and_apply({"flag": "true"}, schema)
    assert result["flag"] is True


def test_validate_number_coercion() -> None:
    schema = [{"name": "count", "type": "number"}]
    result = validate_and_apply({"count": "42"}, schema)
    assert result["count"] == 42.0


def test_validate_enum_valid_value() -> None:
    schema = [{"name": "browser", "type": "enum", "values": ["chromium", "firefox", "webkit"]}]
    result = validate_and_apply({"browser": "firefox"}, schema)
    assert result["browser"] == "firefox"


def test_validate_enum_invalid_value_raises() -> None:
    schema = [{"name": "browser", "type": "enum", "values": ["chromium", "firefox", "webkit"]}]
    with pytest.raises(ValueError, match="must be one of"):
        validate_and_apply({"browser": "safari"}, schema)


def test_workflow_with_input_schema(project_dir: Path) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    wf = textwrap.dedent("""\
        id: schema-test
        inputs:
          - name: env
            type: string
            default: staging
          - name: parallel
            type: boolean
            default: false
        steps:
          - type: shell
            command: echo {{ inputs.env }}
    """)
    _make_workflow(qakit_dir, "schema-test", wf)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("schema-test")
    assert state.status == "completed"
    assert engine.context.inputs.get("env") == "staging"
    assert engine.context.inputs.get("parallel") is False


def test_workflow_required_input_missing_fails(project_dir: Path) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    wf = textwrap.dedent("""\
        id: required-test
        inputs:
          - name: feature
            type: string
            required: true
        steps:
          - type: shell
            command: echo {{ inputs.feature }}
    """)
    _make_workflow(qakit_dir, "required-test", wf)
    engine = WorkflowEngine(project_dir, qakit_dir, non_interactive=True)
    result, state = engine.run("required-test")
    assert result.success is False
    assert state.status == "failed"
