from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from qa_kit_cli._utils import (
    atomic_write,
    find_project_root,
    load_json,
    merge_json,
    save_json,
    sha256_file,
    sha256_text,
)


def test_merge_json_scalar_override() -> None:
    base = {"a": 1, "b": 2}
    override = {"b": 99, "c": 3}
    result = merge_json(base, override)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_merge_json_nested_deep_merge() -> None:
    base = {"outer": {"x": 1, "y": 2}}
    override = {"outer": {"y": 99, "z": 3}}
    result = merge_json(base, override)
    assert result == {"outer": {"x": 1, "y": 99, "z": 3}}


def test_merge_json_does_not_mutate_inputs() -> None:
    base = {"a": 1}
    override = {"a": 2}
    merge_json(base, override)
    assert base["a"] == 1


def test_atomic_write_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "out.txt"
    atomic_write(target, "hello")
    assert target.read_text() == "hello"


def test_atomic_write_removes_tmp_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "out.txt"

    def _boom(self: Path, dest: Path) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(Path, "replace", _boom)
    with pytest.raises(OSError):
        atomic_write(target, "data")
    # No lingering .tmp files
    assert not list(tmp_path.glob("*.tmp"))


def test_sha256_file_consistent(tmp_path: Path) -> None:
    f = tmp_path / "data.bin"
    f.write_bytes(b"abc")
    assert sha256_file(f) == sha256_file(f)


def test_sha256_file_differs_for_different_content(tmp_path: Path) -> None:
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"abc")
    b.write_bytes(b"xyz")
    assert sha256_file(a) != sha256_file(b)


def test_sha256_text_matches_file(tmp_path: Path) -> None:
    text = "hello world"
    f = tmp_path / "t.txt"
    f.write_text(text, encoding="utf-8")
    assert sha256_text(text) == sha256_file(f)


def test_load_json_returns_empty_dict_for_missing_file(tmp_path: Path) -> None:
    result = load_json(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_json_returns_empty_dict_for_invalid_json(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text("not json }{", encoding="utf-8")
    assert load_json(f) == {}


def test_save_and_load_json_roundtrip(tmp_path: Path) -> None:
    data = {"key": "value", "nested": {"n": 1}}
    path = tmp_path / "store.json"
    save_json(path, data)
    assert load_json(path) == data


def test_save_json_ends_with_newline(tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    save_json(path, {"x": 1})
    assert path.read_text().endswith("\n")


def test_find_project_root_finds_qakit_dir(tmp_path: Path) -> None:
    qakit = tmp_path / ".qakit"
    qakit.mkdir()
    nested = tmp_path / "src" / "feature"
    nested.mkdir(parents=True)
    result = find_project_root(nested)
    assert result == tmp_path


def test_find_project_root_returns_none_when_no_qakit(tmp_path: Path) -> None:
    result = find_project_root(tmp_path)
    assert result is None
