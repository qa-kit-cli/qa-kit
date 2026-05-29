"""Workflow execution engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from qa_kit_cli._console import print_info
from qa_kit_cli.extensions import ExtensionManager, HookExecutor
from qa_kit_cli.workflows.base import StepContext, StepResult
from qa_kit_cli.workflows.catalog import WorkflowCatalog
from qa_kit_cli.workflows.expressions import resolve_expressions
from qa_kit_cli.workflows.steps import CommandStep, GateStep, ParallelStep, ShellStep


def _command_to_hook_prefix(command_id: str) -> str | None:
    """Map a qakit command ID to its lifecycle hook prefix.

    "qakit.write.playwright"  → "write_playwright"
    "qakit.ci.github-actions" → "ci_github_actions"
    Returns None for unrecognised or non-qakit command strings.
    """
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
        }
        ext_manager = ExtensionManager(project_root)
        self._active_manifests = ext_manager.active_manifests()
        self._hook_executor = HookExecutor(project_root)

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

    def run(self, workflow_id: str, inputs: dict[str, Any] | None = None) -> StepResult:
        workflow = self._load_workflow(workflow_id)
        self.context.inputs = inputs or {}
        steps = workflow.get("steps", [])
        if not isinstance(steps, list):
            return StepResult(False, "Workflow steps must be a list")

        for idx, step in enumerate(steps, start=1):
            result = self._run_step(step)
            print_info(f"Step {idx}/{len(steps)}: {step.get('id', step.get('type', 'step'))}")
            if not result.success:
                return result
        return StepResult(True, "Workflow completed")

