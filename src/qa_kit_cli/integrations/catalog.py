"""IntegrationCatalog — fetches and queries integrations/catalog.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qa_kit_cli._assets import get_core_pack
from qa_kit_cli._github_http import safe_fetch_json

_COMMUNITY_URL = (
    "https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/integrations/catalog.community.json"
)


def _load_bundled_catalog() -> list[dict[str, Any]]:
    candidates = [
        get_core_pack() / "integrations" / "catalog.json",
        Path(__file__).parent.parent.parent.parent / "integrations" / "catalog.json",
    ]
    for local in candidates:
        if local.exists():
            return json.loads(local.read_text(encoding="utf-8")).get("integrations", [])
    return []


class IntegrationCatalog:
    def __init__(self, include_community: bool = False) -> None:
        self._entries = _load_bundled_catalog()
        if include_community:
            community = safe_fetch_json(_COMMUNITY_URL, {})
            self._entries.extend(community.get("integrations", []))

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [e for e in self._entries if q in e.get("id", "").lower() or q in e.get("name", "").lower()]

    def get(self, integration_id: str) -> dict[str, Any] | None:
        for e in self._entries:
            if e.get("id") == integration_id:
                return e
        return None

    def all(self) -> list[dict[str, Any]]:
        return list(self._entries)
