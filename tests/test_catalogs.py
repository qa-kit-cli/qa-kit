from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from qa_kit_cli.catalogs import CatalogStackBase


def _write_catalog(path: Path, key: str, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({key: items}), encoding="utf-8")


def test_catalog_loads_bundled_entries(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "alpha", "name": "Alpha"}])
    catalog = CatalogStackBase(catalog_path, key="items")
    entries = catalog.all()
    assert len(entries) == 1
    assert entries[0]["id"] == "alpha"


def test_catalog_returns_empty_when_file_missing(tmp_path: Path) -> None:
    catalog = CatalogStackBase(tmp_path / "nonexistent.json", key="items")
    assert catalog.all() == []


def test_catalog_get_by_id(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(
        catalog_path,
        "items",
        [{"id": "alpha", "name": "Alpha"}, {"id": "beta", "name": "Beta"}],
    )
    catalog = CatalogStackBase(catalog_path, key="items")
    item = catalog.get("beta")
    assert item is not None
    assert item["name"] == "Beta"


def test_catalog_get_returns_none_for_missing_id(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "alpha"}])
    catalog = CatalogStackBase(catalog_path, key="items")
    assert catalog.get("nonexistent") is None


def test_catalog_search_matches_id_name_description(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(
        catalog_path,
        "items",
        [
            {"id": "playwright", "name": "Playwright preset", "description": "TypeScript E2E"},
            {"id": "jest", "name": "Jest preset", "description": "Unit testing"},
        ],
    )
    catalog = CatalogStackBase(catalog_path, key="items")
    results = catalog.search("typescript")
    assert len(results) == 1
    assert results[0]["id"] == "playwright"


def test_catalog_search_is_case_insensitive(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "foo", "name": "FooBar", "description": ""}])
    catalog = CatalogStackBase(catalog_path, key="items")
    assert len(catalog.search("foobar")) == 1
    assert len(catalog.search("FOOBAR")) == 1


def test_catalog_community_merge_skipped_without_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "bundled"}])

    fetched: list[str] = []

    def _mock_fetch(url: str, default: Any) -> Any:
        fetched.append(url)
        return {"items": [{"id": "community"}]}

    monkeypatch.setattr("qa_kit_cli.catalogs.safe_fetch_json", _mock_fetch)
    catalog = CatalogStackBase(catalog_path, community_url="https://example.com/c.json", key="items")
    assert len(catalog.all()) == 1
    assert fetched == []


def test_catalog_community_merge_fetches_when_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "bundled"}])

    def _mock_fetch(url: str, default: Any) -> Any:
        return {"items": [{"id": "community"}]}

    monkeypatch.setattr("qa_kit_cli.catalogs.safe_fetch_json", _mock_fetch)
    catalog = CatalogStackBase(
        catalog_path,
        community_url="https://example.com/c.json",
        include_community=True,
        key="items",
    )
    ids = {e["id"] for e in catalog.all()}
    assert ids == {"bundled", "community"}


def test_catalog_community_network_failure_is_silent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_path = tmp_path / "catalog.json"
    _write_catalog(catalog_path, "items", [{"id": "bundled"}])

    def _mock_fetch(url: str, default: Any) -> Any:
        return default  # simulates network failure returning the default

    monkeypatch.setattr("qa_kit_cli.catalogs.safe_fetch_json", _mock_fetch)
    catalog = CatalogStackBase(
        catalog_path,
        community_url="https://example.com/c.json",
        include_community=True,
        key="items",
    )
    assert len(catalog.all()) == 1
    assert catalog.all()[0]["id"] == "bundled"
