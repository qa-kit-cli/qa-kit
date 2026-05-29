from __future__ import annotations

import os
from pathlib import Path

import pytest

import qa_kit_cli.authentication.token_store as ts


@pytest.fixture()
def qakit_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".qakit"
    d.mkdir()
    return d


@pytest.fixture(autouse=True)
def no_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable keyring so all tests exercise the file-based fallback."""
    monkeypatch.setattr(ts, "keyring", None)


class TestGetToken:
    def test_returns_none_when_nothing_stored(self, qakit_dir: Path) -> None:
        assert ts.get_token("jira", qakit_dir) is None

    def test_returns_file_stored_token(self, qakit_dir: Path) -> None:
        ts.set_token("jira", "abc123", qakit_dir)
        assert ts.get_token("jira", qakit_dir) == "abc123"

    def test_env_var_takes_priority_over_file(
        self, qakit_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ts.set_token("jira", "file-value", qakit_dir)
        monkeypatch.setenv("QAKIT_TOKEN_JIRA", "env-value")
        assert ts.get_token("jira", qakit_dir) == "env-value"

    def test_env_var_key_is_uppercased(
        self, qakit_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("QAKIT_TOKEN_TESTRAIL", "tr-token")
        assert ts.get_token("testrail", qakit_dir) == "tr-token"

    def test_env_var_hyphen_converted_to_underscore(
        self, qakit_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("QAKIT_TOKEN_ALLURE_REPORTER", "allure-val")
        assert ts.get_token("allure-reporter", qakit_dir) == "allure-val"


class TestSetToken:
    def test_persists_token_to_file(self, qakit_dir: Path) -> None:
        ts.set_token("testrail", "tr-secret", qakit_dir)
        store_path = qakit_dir / "auth" / "tokens.json"
        assert store_path.exists()
        content = store_path.read_text()
        assert "tr-secret" in content

    def test_multiple_services_stored_independently(self, qakit_dir: Path) -> None:
        ts.set_token("jira", "j-token", qakit_dir)
        ts.set_token("testrail", "t-token", qakit_dir)
        assert ts.get_token("jira", qakit_dir) == "j-token"
        assert ts.get_token("testrail", qakit_dir) == "t-token"

    def test_overwrite_existing_token(self, qakit_dir: Path) -> None:
        ts.set_token("jira", "old", qakit_dir)
        ts.set_token("jira", "new", qakit_dir)
        assert ts.get_token("jira", qakit_dir) == "new"


class TestDeleteToken:
    def test_deletes_stored_token(self, qakit_dir: Path) -> None:
        ts.set_token("jira", "abc", qakit_dir)
        ts.delete_token("jira", qakit_dir)
        assert ts.get_token("jira", qakit_dir) is None

    def test_delete_nonexistent_token_is_silent(self, qakit_dir: Path) -> None:
        ts.delete_token("nonexistent", qakit_dir)  # must not raise

    def test_delete_leaves_other_tokens_intact(self, qakit_dir: Path) -> None:
        ts.set_token("jira", "j", qakit_dir)
        ts.set_token("testrail", "t", qakit_dir)
        ts.delete_token("jira", qakit_dir)
        assert ts.get_token("testrail", qakit_dir) == "t"
        assert ts.get_token("jira", qakit_dir) is None


class TestKeyringFallback:
    def test_keyring_token_returned_when_available(
        self, qakit_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_keyring = type(
            "MockKeyring",
            (),
            {
                "get_password": staticmethod(lambda svc, key: "kr-value"),
                "set_password": staticmethod(lambda svc, key, val: None),
                "delete_password": staticmethod(lambda svc, key: None),
            },
        )
        monkeypatch.setattr(ts, "keyring", mock_keyring)
        result = ts.get_token("jira", qakit_dir)
        assert result == "kr-value"

    def test_keyring_set_skips_file_write(
        self, qakit_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_keyring = type(
            "MockKeyring",
            (),
            {
                "get_password": staticmethod(lambda svc, key: None),
                "set_password": staticmethod(lambda svc, key, val: None),
                "delete_password": staticmethod(lambda svc, key: None),
            },
        )
        monkeypatch.setattr(ts, "keyring", mock_keyring)
        ts.set_token("jira", "secret", qakit_dir)
        store_path = qakit_dir / "auth" / "tokens.json"
        # keyring succeeded so file fallback should not be written
        assert not store_path.exists() or "secret" not in store_path.read_text()
