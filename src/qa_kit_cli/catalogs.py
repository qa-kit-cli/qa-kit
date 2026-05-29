"""Catalog stack abstractions for integrations, presets, extensions, and workflows."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    from platformdirs import user_config_dir as _platform_user_config_dir
except Exception:  # pragma: no cover - fallback for minimal environments
    def _platform_user_config_dir(appname: str) -> str:
        return str(Path.home() / ".config" / appname)

from qa_kit_cli._assets import get_core_pack
from qa_kit_cli._github_http import safe_fetch_json


_FETCH_FAILED = object()


def user_config_dir(appname: str) -> str:
    return _platform_user_config_dir(appname)


@dataclass(frozen=True)
class CatalogSource:
    name: str
    source: str
    source_type: str  # "remote" | "file"
    priority: int


class CatalogStackBase:
    """Resolve and query catalog entries with a 4-source precedence stack."""

    def __init__(
        self,
        bundled_catalog: Path,
        community_url: str | None = None,
        include_community: bool = False,
        key: str = "items",
        *,
        env_vars: tuple[str, ...] = (),
        config_key: str | None = None,
        community_catalog: Path | None = None,
    ) -> None:
        self._key = key
        self._bundled_catalog = bundled_catalog
        self._community_catalog = community_catalog
        self._community_url = community_url
        self._include_community = include_community
        self._env_vars = env_vars
        self._config_key = config_key
        self.last_remote_failed = False

        # Backward-compat mode for existing tests that instantiate with only bundled path.
        self._legacy_mode = not env_vars and config_key is None
        self._entries: list[dict[str, Any]] = []
        if self._legacy_mode:
            self._entries.extend(self._load_file_entries(bundled_catalog))
            if include_community:
                if community_catalog is not None:
                    self._entries.extend(self._load_file_entries(community_catalog))
                elif community_url:
                    self._entries.extend(self._load_remote_entries(community_url))

    def _load_file_entries(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return list(data.get(self._key, []))

    def _load_remote_entries(self, url: str) -> list[dict[str, Any]]:
        data = safe_fetch_json(url, _FETCH_FAILED)
        if data is _FETCH_FAILED or not isinstance(data, dict):
            self.last_remote_failed = True
            return []
        return list(data.get(self._key, []))

    def _source_entries(self, source: CatalogSource) -> list[dict[str, Any]]:
        if source.source_type == "file":
            return self._load_file_entries(Path(source.source))
        return self._load_remote_entries(source.source)

    def _read_catalog_url(self, config_path: Path) -> str | None:
        if not self._config_key or not config_path.exists():
            return None
        try:
            data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return None

        keys = [self._config_key]
        if self._config_key.endswith("s"):
            keys.append(self._config_key[:-1])
        keys.append(f"{self._config_key}_catalog_url")

        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
            if isinstance(value, dict):
                url = value.get("url")
                if isinstance(url, str) and url:
                    return url
        return None

    def resolve_sources(self) -> list[CatalogSource]:
        if self._legacy_mode:
            return [
                CatalogSource(
                    name="bundled",
                    source=str(self._bundled_catalog),
                    source_type="file",
                    priority=4,
                )
            ]

        sources: list[CatalogSource] = []

        # 1) Environment variables (highest)
        for env_key in self._env_vars:
            env_url = os.environ.get(env_key, "").strip()
            if env_url:
                sources.append(
                    CatalogSource(
                        name=f"env:{env_key}",
                        source=env_url,
                        source_type="remote",
                        priority=1,
                    )
                )

        # 2) Project catalog config (.qakit/catalogs.yml)
        project_cfg = Path.cwd() / ".qakit" / "catalogs.yml"
        project_url = self._read_catalog_url(project_cfg)
        if project_url:
            sources.append(
                CatalogSource(
                    name="project:.qakit/catalogs.yml",
                    source=project_url,
                    source_type="remote",
                    priority=2,
                )
            )

        # 3) User catalog config (<user_config_dir>/catalogs.yml)
        user_cfg = Path(user_config_dir("qa-kit")) / "catalogs.yml"
        user_url = self._read_catalog_url(user_cfg)
        if user_url:
            sources.append(
                CatalogSource(
                    name="user:catalogs.yml",
                    source=user_url,
                    source_type="remote",
                    priority=3,
                )
            )

        # 4) Bundled catalogs (always present fallback)
        sources.append(
            CatalogSource(
                name="bundled",
                source=str(self._bundled_catalog),
                source_type="file",
                priority=4,
            )
        )
        if self._community_catalog is not None:
            sources.append(
                CatalogSource(
                    name="bundled-community",
                    source=str(self._community_catalog),
                    source_type="file",
                    priority=4,
                )
            )
        elif self._community_url and self._include_community:
            sources.append(
                CatalogSource(
                    name="community-remote",
                    source=self._community_url,
                    source_type="remote",
                    priority=4,
                )
            )

        return sources

    def _merged_entries(self) -> list[dict[str, Any]]:
        if self._legacy_mode:
            return list(self._entries)

        self.last_remote_failed = False
        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for source in self.resolve_sources():
            for entry in self._source_entries(source):
                entry_id = str(entry.get("id", "")).strip()
                if not entry_id or entry_id in seen:
                    continue
                seen.add(entry_id)
                enriched = dict(entry)
                enriched.setdefault("_source", source.name)
                enriched.setdefault("_source_ref", source.source)
                merged.append(enriched)
        return merged

    def all(self) -> list[dict[str, Any]]:
        return self._merged_entries()

    def get(self, item_id: str) -> dict[str, Any] | None:
        for item in self._merged_entries():
            if item.get("id") == item_id:
                return item
        return None

    def search(self, query: str) -> list[dict[str, Any]]:
        q = (query or "").strip().lower()
        entries = self._merged_entries()
        if not q:
            return entries
        out: list[dict[str, Any]] = []
        for item in entries:
            tags = item.get("tags", [])
            if isinstance(tags, list):
                tags_blob = " ".join(str(t) for t in tags)
            else:
                tags_blob = str(tags)
            hay = " ".join(
                [
                    str(item.get("id", "")),
                    str(item.get("name", "")),
                    str(item.get("description", "")),
                    tags_blob,
                ]
            ).lower()
            if q in hay:
                out.append(item)
        return out


class IntegrationCatalogStack(CatalogStackBase):
    def __init__(self, _: Path | None = None, include_community: bool = True) -> None:
        core = get_core_pack()
        super().__init__(
            bundled_catalog=core / "integrations" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/integrations/catalog.community.json",
            include_community=include_community,
            key="integrations",
            env_vars=("QAKIT_INT_CATALOG_URL", "QAKIT_CATALOG_URL"),
            config_key="integrations",
            community_catalog=core / "integrations" / "catalog.community.json",
        )


class ExtensionCatalogStack(CatalogStackBase):
    def __init__(self, _: Path | None = None, include_community: bool = True) -> None:
        core = get_core_pack()
        super().__init__(
            bundled_catalog=core / "extensions" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/extensions/catalog.community.json",
            include_community=include_community,
            key="extensions",
            env_vars=("QAKIT_EXT_CATALOG_URL", "QAKIT_CATALOG_URL"),
            config_key="extensions",
            community_catalog=core / "extensions" / "catalog.community.json",
        )


class PresetCatalogStack(CatalogStackBase):
    def __init__(self, _: Path | None = None, include_community: bool = True) -> None:
        core = get_core_pack()
        super().__init__(
            bundled_catalog=core / "presets" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/presets/catalog.community.json",
            include_community=include_community,
            key="presets",
            env_vars=("QAKIT_PRESET_CATALOG_URL", "QAKIT_CATALOG_URL"),
            config_key="presets",
            community_catalog=core / "presets" / "catalog.community.json",
        )


class WorkflowCatalogStack(CatalogStackBase):
    def __init__(self, _: Path | None = None, include_community: bool = True) -> None:
        core = get_core_pack()
        super().__init__(
            bundled_catalog=core / "workflows" / "catalog.json",
            community_url="https://raw.githubusercontent.com/qa-kit-cli/qa-kit/main/workflows/catalog.community.json",
            include_community=include_community,
            key="workflows",
            env_vars=("QAKIT_WORKFLOW_CATALOG_URL",),
            config_key="workflows",
            community_catalog=core / "workflows" / "catalog.community.json",
        )
