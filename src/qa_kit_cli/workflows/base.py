"""Workflow base abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StepContext:
    project_root: Path
    qakit_dir: Path
    inputs: dict[str, Any] = field(default_factory=dict)
    non_interactive: bool = False


@dataclass
class StepResult:
    success: bool
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    paused: bool = False  # True when a gate step explicitly pauses the workflow


class StepBase(ABC):
    @abstractmethod
    def run(self, step: dict[str, Any], context: StepContext) -> StepResult:
        """Run a step and return its result."""

