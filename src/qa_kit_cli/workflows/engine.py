"""Workflow execution engine with persistent run state."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from qa_kit_cli._console import print_info
from qa_kit_cli.extensions import ExtensionManager, HookExecutor
from qa_kit_cli.workflows.base import StepContext, StepResult
from qa_kit_cli.workflows.catalog import WorkflowCatalog
from qa_kit_cli.workflows.expressions import resolve_expressions
from qa_kit_cli.workflows.run_state import RunState, list_runs
from qa_kit_cli.workflows.steps import CommandStep, GateStep, IfStep, ParallelStep, ShellStep


def _command_to_hook_prefix(command_id: str) -> str | None:
    if not command_id.startswith("qakit."):
        return None
    suffix = command_id[len("qakit."):]
    return suffix.replace(".", "_").replace("-", "_")


class WorkflowEngine:
    def __init__(self, project_root: Path, qakit_dir: Path, non_interactive: bool = True) -> None:
        self.project_root = project_root
        self.qakit_dir = qakit_dir
        self.catalog = WorkflowCatalog(project_root, qakit_dir)
        self.context = StepContext(project_root, qakit_dir, inputs={}, non_interactive=non_interactive)
        self._dispatch = {
            "command": CommandStep(),
            "shell": ShellStep(),
            "gate": GateStep(),
            "parallel": ParallelStep(),
            "if": IfStep(),
        }
        ext_manager = ExtensionManager(project_root)
        self._active_manifests = ext_manager.active_manifests()
        self._hook_executor = HookExecutor(project_root)
        self._runs_dir = qakit_dir / "workflows" / "runs"

    def _load_workflow(self, workflow_id: str) -> dict[str, Any]:
        path = self.catalog.get_path(workflow_id)
        if path is None:
            raise FileNotFoundError(f"Workflow not found: {workflow_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _run_step(self, step: dict[str, Any]) -> StepResult:
        step_type = str(step.get("type", "command"))
        runner = self._dispatch.get(step_type)
        if runner is None:
            return StepResult(False, f"Unsupported step type: {step_type}")
        resolved = resolve_expressions(step, self.context.inputs)

        hook_prefix: str | None = None
        if step_type == "command":
            hook_prefix = _command_to_hook_prefix(str(resolved.get("command", "")))
            if hook_prefix:
                self._hook_executor.execute(self._active_manifests, f"before_{hook_prefix}")

        result = runner.run(resolved, self.context)

        if hook_prefix and result.success:
            self._hook_executor.execute(self._active_manifests, f"after_{hook_prefix}")

        return result

    def run(
        self,
        workflow_id: str,
        inputs: dict[str, Any] | None = None,
        run_state: RunState | None = None,
    ) -> tuple[StepResult, RunState]:
        workflow = self._load_workflow(workflow_id)
        effective_inputs = inputs or {}
        self.context.inputs = effective_inputs

        state = run_state or RunState.new(workflow_id, effective_inputs)
        state.save(self._runs_dir)

        steps = workflow.get("steps", [])
        if not isinstance(steps, list):
            state.status = "failed"
            state.save(self._runs_dir)
            return StepResult(False, "Workflow steps must be a list"), state

        start_idx = state.current_step
        for idx, step in enumerate(steps[start_idx:], start=start_idx + 1):
            step_id = step.get("id", step.get("type", "step"))
            print_info(f"Step {idx}/{len(steps)}: {step_id}")
            result = self._run_step(step)
            state.current_step = idx
            state.append_log(self._runs_dir, {"step": step_id, "success": result.success, "output": result.output})

            if not result.success:
                state.status = "failed"
                state.save(self._runs_dir)
                return result, state

            if isinstance(runner := self._dispatch.get(str(step.get("type", "command"))), GateStep):
                # Gate step that paused
                if not result.success:
                    state.status = "paused"
                    state.save(self._runs_dir)
                    return result, state

        state.status = "completed"
        state.save(self._runs_dir)
        return StepResult(True, "Workflow completed"), state

    def resume(self, run_id: str) -> tuple[StepResult, RunState]:
        run_dir = self._runs_dir / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run '{run_id}' not found.")
        state = RunState.load(run_dir)
        if state.status == "completed":
            return StepResult(True, "Already completed"), state
        return self.run(state.workflow_id, state.inputs, run_state=state)

    def get_run(self, run_id: str) -> RunState | None:
        run_dir = self._runs_dir / run_id
        if not run_dir.exists():
            return None
        return RunState.load(run_dir)

    def list_runs(self) -> list[RunState]:
        return list_runs(self._runs_dir)
