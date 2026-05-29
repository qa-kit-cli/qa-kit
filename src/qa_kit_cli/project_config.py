"""Read/write the .qakit/config.json project configuration file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qa_kit_cli._utils import load_json, save_json

_SCHEMA_VERSION = 1
_FILENAME = "config.json"


@dataclass
class ProjectConfig:
    """Project configuration stored in .qakit/config.json."""

    schema_version: int = _SCHEMA_VERSION
    script: str = "ps"
    branch_numbering: str = "sequential"
    created_by: str = "qa-kit-cli"
    active_suite: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, qakit_dir: Path) -> "ProjectConfig":
        """Load configuration from .qakit/config.json, returning defaults if absent."""
        data = load_json(qakit_dir / _FILENAME)
        known = {"schema_version", "script", "branch_numbering", "created_by", "active_suite"}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(
            schema_version=int(data.get("schema_version", _SCHEMA_VERSION)),
            script=str(data.get("script", "ps")),
            branch_numbering=str(data.get("branch_numbering", "sequential")),
            created_by=str(data.get("created_by", "qa-kit-cli")),
            active_suite=data.get("active_suite") or None,
            extra=extra,
        )

    def save(self, qakit_dir: Path) -> None:
        """Persist configuration to .qakit/config.json."""
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "script": self.script,
            "branch_numbering": self.branch_numbering,
            "created_by": self.created_by,
        }
        if self.active_suite is not None:
            data["active_suite"] = self.active_suite
        data.update(self.extra)
        save_json(qakit_dir / _FILENAME, data)
