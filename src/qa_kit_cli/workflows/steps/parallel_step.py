"""Parallel fan-out step."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult
from qa_kit_cli.workflows.steps.command_step import CommandStep
from qa_kit_cli.workflows.steps.gate_step import GateStep
from qa_kit_cli.workflows.steps.shell_step import ShellStep


class ParallelStep(StepBase):
    def __init__(self) -> None:
        self._dispatch = {
            "command": CommandStep(),
            "shell": ShellStep(),
            "gate": GateStep(),
        }

    def _run_one(self, substep: dict[str, Any], context: StepContext) -> StepResult:
        step_type = str(substep.get("type", "shell"))
        runner = self._dispatch.get(step_type)
        if runner is None:
            return StepResult(False, f"Unsupported substep type: {step_type}")
        return runner.run(substep, context)

    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        substeps = step.get("steps", [])
        if not isinstance(substeps, list) or not substeps:
            return StepResult(False, "Parallel step requires non-empty steps list")

        outputs: list[str] = []
        ok = True
        with ThreadPoolExecutor(max_workers=min(8, len(substeps))) as pool:
            futures = [pool.submit(self._run_one, substep, context) for substep in substeps]
            for future in as_completed(futures):
                result = future.result()
                ok = ok and result.success
                if result.output:
                    outputs.append(result.output)
        return StepResult(ok, "\n".join(outputs))

