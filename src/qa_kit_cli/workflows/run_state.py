"""Persistent workflow run state."""

from __future__ import annotations

import contextlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class RunState:
    run_id: str
    workflow_id: str
    status: str  # "running" | "paused" | "completed" | "failed"
    current_step: int
    inputs: dict[str, Any]
    outputs: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def new(cls, workflow_id: str, inputs: dict[str, Any]) -> RunState:
        now = _now()
        return cls(
            run_id=uuid.uuid4().hex[:8],
            workflow_id=workflow_id,
            status="running",
            current_step=0,
            inputs=inputs,
            outputs={},
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def load(cls, run_dir: Path) -> RunState:
        data = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, runs_dir: Path) -> Path:
        run_dir = runs_dir / self.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        self.updated_at = _now()
        (run_dir / "state.json").write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "workflow_id": self.workflow_id,
                    "status": self.status,
                    "current_step": self.current_step,
                    "inputs": self.inputs,
                    "outputs": self.outputs,
                    "created_at": self.created_at,
                    "updated_at": self.updated_at,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_dir / "inputs.json").write_text(
            json.dumps(self.inputs, indent=2), encoding="utf-8"
        )
        return run_dir

    def append_log(self, runs_dir: Path, entry: dict[str, Any]) -> None:
        log_path = runs_dir / self.run_id / "log.jsonl"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**entry, "ts": _now()}) + "\n")


def list_runs(runs_dir: Path) -> list[RunState]:
    if not runs_dir.exists():
        return []
    states: list[RunState] = []
    for run_dir in sorted(runs_dir.iterdir()):
        state_file = run_dir / "state.json"
        if state_file.exists():
            with contextlib.suppress(Exception):
                states.append(RunState.load(run_dir))
    return sorted(states, key=lambda r: r.created_at, reverse=True)
