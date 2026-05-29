"""Catalog stack abstractions for integrations, presets, and extensions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qa_kit_cli._github_http import safe_fetch_json


class CatalogStackBase:
    """Load a bundled catalog and optionally merge community catalog entries."""

    def __init__(
        self,
        bundled_catalog: Path,
        community_url: str | None = None,
        include_community: bool = False,
        key: str = "items",
    ) -> None:
        self._key = key
        self._entries: list[dict[str, Any]] = []
        self._load_bundled(bundled_catalog)
        if include_community and community_url:
            self._load_community(community_url)

    def _load_bundled(self, path: Path) -> None:
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self._entries.extend(data.get(self._key, []))

    def _load_community(self, url: str) -> None:
        data = safe_fetch_json(url, {})
        self._entries.extend(data.get(self._key, []))

    def all(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def get(self, item_id: str) -> dict[str, Any] | None:
        for item in self._entries:
            if item.get("id") == item_id:
                return item
        return None

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        out: list[dict[str, Any]] = []
        for item in self._entries:
            hay = " ".join(str(item.get(k, "")) for k in ("id", "name", "description")).lower()
            if q in hay:
                out.append(item)
        return out


class IntegrationCatalogStack(CatalogStackBase):
    def __init__(self, project_root: Path, include_community: bool = False) -> None:
        super().__init__(
            bundled_catalog=project_root / "integrations" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/integrations/catalog.community.json",
            include_community=include_community,
            key="integrations",
        )


class ExtensionCatalogStack(CatalogStackBase):
    def __init__(self, project_root: Path, include_community: bool = False) -> None:
        super().__init__(
            bundled_catalog=project_root / "extensions" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/extensions/catalog.community.json",
            include_community=include_community,
            key="extensions",
        )


class PresetCatalogStack(CatalogStackBase):
    def __init__(self, project_root: Path, include_community: bool = False) -> None:
        super().__init__(
            bundled_catalog=project_root / "presets" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/presets/catalog.community.json",
            include_community=include_community,
            key="presets",
        )
