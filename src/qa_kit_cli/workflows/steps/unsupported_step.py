"""Stubs for step types that are schema-recognised but not yet fully implemented."""

from __future__ import annotations

from typing import Any

from qa_kit_cli.workflows.base import StepBase, StepContext, StepResult


class UnsupportedStep(StepBase):
    """Placeholder for step types declared in workflow YAML but not yet implemented."""

    def __init__(self, step_type: str) -> None:
        self._type = step_type

    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        return StepResult(
            success=False,
            output=(
                f"Step type '{self._type}' is declared in the workflow schema but is not yet "
                "fully implemented. Add command/shell/gate/if steps as an alternative, or "
                "implement the step type to continue."
            ),
        )


class PromptStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("prompt")


class SwitchStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("switch")


class WhileStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("while")


class DoWhileStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("do-while")


class FanOutStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("fan-out")


class FanInStep(UnsupportedStep):
    def __init__(self) -> None:
        super().__init__("fan-in")
