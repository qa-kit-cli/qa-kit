"""Conditional workflow step."""

from __future__ import annotations

from typing import Any

from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult


class IfStep(StepBase):
    """Run a 'then' or 'else' branch based on an input condition value."""

    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        condition = str(step.get("condition", ""))
        then_steps: list[dict[str, Any]] = step.get("then", [])
        else_steps: list[dict[str, Any]] = step.get("else", [])

        raw = context.inputs.get(condition, condition)
        truthy = bool(raw) and str(raw).lower() not in ("false", "0", "no", "")

        branch = then_steps if truthy else else_steps
        if not branch:
            return StepResult(True, f"if '{condition}' → no branch to run")

        from qa_kit_cli.workflows.engine import WorkflowEngine  # local import to avoid cycle

        engine = WorkflowEngine.__new__(WorkflowEngine)
        engine.project_root = context.project_root
        engine.qakit_dir = context.qakit_dir
        engine.context = context

        from qa_kit_cli.workflows.steps import CommandStep, GateStep, ParallelStep, ShellStep

        engine._dispatch = {
            "command": CommandStep(),
            "shell": ShellStep(),
            "gate": GateStep(),
            "parallel": ParallelStep(),
            "if": IfStep(),
        }
        from qa_kit_cli.extensions import ExtensionManager, HookExecutor

        ext_manager = ExtensionManager(context.project_root)
        engine._active_manifests = ext_manager.active_manifests()
        engine._hook_executor = HookExecutor(context.project_root)

        for sub_step in branch:
            result = engine._run_step(sub_step)
            if not result.success:
                return result

        return StepResult(True, f"if '{condition}' → branch completed")
