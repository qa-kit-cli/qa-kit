"""Read/write the .qakit/integration.json state file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qa_kit_cli._utils import load_json, save_json

_SCHEMA_VERSION = 1
_FILENAME = "integration.json"


@dataclass
class IntegrationState:
    active_key: str = ""
    installed: dict[str, dict[str, Any]] = field(default_factory=dict)
    schema_version: int = _SCHEMA_VERSION

    @classmethod
    def load(cls, qakit_dir: Path) -> "IntegrationState":
        data = load_json(qakit_dir / _FILENAME)
        return cls(
            active_key=data.get("active_key", ""),
            installed=data.get("installed", {}),
            schema_version=data.get("schema_version", _SCHEMA_VERSION),
        )

    def save(self, qakit_dir: Path) -> None:
        save_json(
            qakit_dir / _FILENAME,
            {
                "schema_version": self.schema_version,
                "active_key": self.active_key,
                "installed": self.installed,
            },
        )

    def add(self, key: str, meta: dict[str, Any]) -> None:
        self.installed[key] = meta

    def remove(self, key: str) -> None:
        self.installed.pop(key, None)

    def is_installed(self, key: str) -> bool:
        return key in self.installed

    def set_active(self, key: str) -> None:
        self.active_key = key
