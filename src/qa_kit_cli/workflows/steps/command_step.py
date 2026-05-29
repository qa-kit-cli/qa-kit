"""Dispatches a slash-command style step."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult


class CommandStep(StepBase):
    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        command = str(step.get("command", "")).strip()
        if not command:
            return StepResult(False, "Missing command step.command")

        run_dir = context.qakit_dir / "workflow-runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        log = run_dir / "commands.log"
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(command + "\n")
        return StepResult(True, f"Dispatched {command}")

