from __future__ import annotations

from pathlib import Path

from qa_kit_cli.catalogs import ExtensionCatalogStack
from qa_kit_cli.shared_infra import ensure_project_layout


def test_env_var_catalog_takes_priority(project_dir: Path, tmp_path: Path, monkeypatch) -> None:
    ensure_project_layout(project_dir)
    (project_dir / ".qakit" / "catalogs.yml").write_text(
        "extensions:\n  url: https://project.example/extensions.json\n",
        encoding="utf-8",
    )
    user_cfg_dir = tmp_path / "usercfg"
    user_cfg_dir.mkdir(parents=True)
    (user_cfg_dir / "catalogs.yml").write_text(
        "extensions:\n  url: https://user.example/extensions.json\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("qa_kit_cli.catalogs.user_config_dir", lambda appname: str(user_cfg_dir))
    monkeypatch.setenv("QAKIT_EXT_CATALOG_URL", "https://env.example/extensions.json")

    stack = ExtensionCatalogStack(project_dir)
    sources = stack.resolve_sources()
    assert sources[0].source == "https://env.example/extensions.json"


def test_project_catalog_overrides_user(project_dir: Path, tmp_path: Path, monkeypatch) -> None:
    ensure_project_layout(project_dir)
    (project_dir / ".qakit" / "catalogs.yml").write_text(
        "extensions:\n  url: https://project.example/extensions.json\n",
        encoding="utf-8",
    )
    user_cfg_dir = tmp_path / "usercfg"
    user_cfg_dir.mkdir(parents=True)
    (user_cfg_dir / "catalogs.yml").write_text(
        "extensions:\n  url: https://user.example/extensions.json\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("qa_kit_cli.catalogs.user_config_dir", lambda appname: str(user_cfg_dir))

    stack = ExtensionCatalogStack(project_dir)
    sources = stack.resolve_sources()
    assert sources[0].source == "https://project.example/extensions.json"
    assert sources[1].source == "https://user.example/extensions.json"


def test_bundled_catalog_is_last_resort(project_dir: Path) -> None:
    ensure_project_layout(project_dir)
    stack = ExtensionCatalogStack(project_dir)
    sources = stack.resolve_sources()
    assert sources[-2].name == "bundled"
    assert sources[-1].name == "bundled-community"
