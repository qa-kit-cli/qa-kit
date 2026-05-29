"""Runs a shell command workflow step."""

from __future__ import annotations

import subprocess
from typing import Any

from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult


class ShellStep(StepBase):
    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        command = str(step.get("run") or step.get("command") or "").strip()
        if not command:
            return StepResult(False, "Missing shell step run/command")

        result = subprocess.run(
            command,
            cwd=context.project_root,
            shell=True,
            text=True,
            capture_output=True,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return StepResult(result.returncode == 0, output.strip())

