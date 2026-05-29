from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.catalogs import ExtensionCatalogStack
from qa_kit_cli.shared_infra import ensure_project_layout


def test_extension_search_bundled(project_dir: Path) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    result = runner.invoke(app, ["extension", "search", "allure"])
    assert result.exit_code == 0, result.output
    assert "allure" in result.output.lower()


def test_extension_search_remote_fallback(project_dir: Path, monkeypatch) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    monkeypatch.setenv("QAKIT_EXT_CATALOG_URL", "https://invalid.example/catalog.json")
    monkeypatch.setattr("qa_kit_cli.catalogs.safe_fetch_json", lambda url, default=None: default)

    result = runner.invoke(app, ["extension", "search", "git"])
    assert result.exit_code == 0, result.output
    assert "Using bundled catalog (remote fetch failed)" in result.output
    assert "git" in result.output.lower()


def test_catalog_resolution_order(project_dir: Path, tmp_path: Path, monkeypatch) -> None:
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
    assert sources[1].source == "https://project.example/extensions.json"
    assert sources[2].source == "https://user.example/extensions.json"
