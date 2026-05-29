"""Workflow catalog (bundled + project-local)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from qa_kit_cli._assets import get_bundled_workflows_dir


class WorkflowCatalog:
    def __init__(self, project_root: Path, qakit_dir: Path) -> None:
        self.project_root = project_root
        self.qakit_dir = qakit_dir
        self.bundled_dir = get_bundled_workflows_dir()
        self.local_dir = qakit_dir / "workflows"

    def _candidates(self) -> list[Path]:
        return [self.local_dir, self.bundled_dir]

    def list(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        seen: set[str] = set()
        for base in self._candidates():
            if not base.exists():
                continue
            for workflow_file in base.rglob("workflow.yml"):
                data = yaml.safe_load(workflow_file.read_text(encoding="utf-8")) or {}
                workflow_id = str(data.get("id", workflow_file.parent.name))
                if workflow_id in seen:
                    continue
                seen.add(workflow_id)
                entries.append({"id": workflow_id, "path": workflow_file})
        return sorted(entries, key=lambda x: x["id"])

    def get_path(self, workflow_id: str) -> Path | None:
        for item in self.list():
            if item["id"] == workflow_id:
                return Path(item["path"])
        return None

