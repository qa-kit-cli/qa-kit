"""Read/write the .qakit/integration.json state file with schema migration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qa_kit_cli._utils import load_json, save_json
from qa_kit_cli._version import __version__

_SCHEMA_VERSION = 2
_FILENAME = "integration.json"


def _migrate_v1(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate schema_version 1 (or unversioned) → 2.

    Old layout:
      { "active_key": "claude", "installed": { "claude": {...} }, "schema_version": 1 }
    New layout:
      { "schema_version": 2, "qakit_version": "...", "active_integration": "claude",
        "installed_integrations": ["claude"], "integration_settings": { "claude": {...} } }
    """
    active = data.get("active_key", "")
    installed_dict: dict[str, Any] = data.get("installed", {})
    return {
        "schema_version": _SCHEMA_VERSION,
        "qakit_version": data.get("qakit_version", __version__),
        "active_integration": active,
        "installed_integrations": list(installed_dict.keys()),
        "integration_settings": installed_dict,
    }


@dataclass
class IntegrationState:
    active_key: str = ""
    installed: dict[str, dict[str, Any]] = field(default_factory=dict)
    schema_version: int = _SCHEMA_VERSION
    qakit_version: str = ""

    @classmethod
    def load(cls, qakit_dir: Path) -> IntegrationState:
        data = load_json(qakit_dir / _FILENAME)
        ver = int(data.get("schema_version", 1))

        # Migrate old schema
        if ver < _SCHEMA_VERSION or "active_key" in data:
            data = _migrate_v1(data)

        return cls(
            active_key=data.get("active_integration", data.get("active_key", "")),
            installed=data.get("integration_settings", data.get("installed", {})),
            schema_version=int(data.get("schema_version", _SCHEMA_VERSION)),
            qakit_version=data.get("qakit_version", __version__),
        )

    def save(self, qakit_dir: Path) -> None:
        save_json(
            qakit_dir / _FILENAME,
            {
                "schema_version": _SCHEMA_VERSION,
                "qakit_version": self.qakit_version or __version__,
                "active_integration": self.active_key,
                "installed_integrations": list(self.installed.keys()),
                "integration_settings": self.installed,
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
