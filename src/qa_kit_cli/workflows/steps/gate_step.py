"""Interactive gate step."""

from __future__ import annotations

from typing import Any

from qa_kit_cli._console import confirm
from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult


class GateStep(StepBase):
    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        prompt = str(step.get("prompt", "Continue workflow?"))
        if context.non_interactive:
            allowed = bool(step.get("default", True))
        else:
            allowed = confirm(prompt, default=bool(step.get("default", True)))
        return StepResult(allowed, "approved" if allowed else "rejected")

