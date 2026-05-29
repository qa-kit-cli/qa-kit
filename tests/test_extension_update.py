from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from qa_kit_cli import app
from qa_kit_cli.shared_infra import ensure_project_layout


def _make_fake_extension(tmp_path: Path, version: str) -> Path:
    ext_dir = tmp_path / "git-fake"
    (ext_dir / "templates" / "commands").mkdir(parents=True)
    (ext_dir / "extension.yml").write_text(
        "\n".join(
            [
                "id: git",
                "name: Git Workflow",
                f"version: {version}",
                "description: Fake update source",
                "hooks:",
                "  - after_strategy",
                "commands:",
                "  after_strategy: \"echo updated\"",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ext_dir / "templates" / "commands" / "qakit.strategy.md").write_text(
        "updated template content",
        encoding="utf-8",
    )
    return ext_dir


def test_extension_update_upgrades_version(project_dir: Path, tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    add_result = runner.invoke(app, ["extension", "add", "git"])
    assert add_result.exit_code == 0, add_result.output

    fake_src = _make_fake_extension(tmp_path, "0.1.1")
    monkeypatch.setattr("qa_kit_cli.extensions.ExtensionRegistry.resolve", lambda self, ref: fake_src)

    result = runner.invoke(app, ["extension", "update", "git"])
    assert result.exit_code == 0, result.output
    assert "Updated git from v0.1.0" in result.output
    assert "v0.1.1" in result.output

    state = json.loads((project_dir / ".qakit" / "extensions.json").read_text(encoding="utf-8"))
    git_entry = next(e for e in state["extensions"] if e["id"] == "git")
    assert git_entry["version"] == "0.1.1"


def test_extension_update_already_latest(project_dir: Path) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    add_result = runner.invoke(app, ["extension", "add", "git"])
    assert add_result.exit_code == 0, add_result.output

    result = runner.invoke(app, ["extension", "update", "git"])
    assert result.exit_code == 0, result.output
    assert "Already at latest version" in result.output


def test_extension_update_preserves_config(project_dir: Path, tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    ensure_project_layout(project_dir)
    add_result = runner.invoke(app, ["extension", "add", "git"])
    assert add_result.exit_code == 0, add_result.output

    cfg_path = project_dir / ".qakit" / "extensions" / "git" / "config.local.json"
    cfg_path.write_text('{"keep": true}', encoding="utf-8")

    fake_src = _make_fake_extension(tmp_path, "0.1.2")
    monkeypatch.setattr("qa_kit_cli.extensions.ExtensionRegistry.resolve", lambda self, ref: fake_src)

    result = runner.invoke(app, ["extension", "update", "git"])
    assert result.exit_code == 0, result.output
    assert cfg_path.exists()
    assert cfg_path.read_text(encoding="utf-8") == '{"keep": true}'
