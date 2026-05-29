"""Secure storage for third-party service tokens (Jira, TestRail, Allure)."""

from __future__ import annotations

import os
from pathlib import Path

from qa_kit_cli._utils import load_json, save_json


_STORE_FILE = "tokens.json"
_ENV_PREFIX = "QAKIT_TOKEN_"
_KEYRING_SERVICE = "qa-kit-cli"

try:
    import keyring
except Exception:  # pragma: no cover - optional dependency/environment specific
    keyring = None  # type: ignore[assignment]


def _store_path(qakit_dir: Path) -> Path:
    return qakit_dir / "auth" / _STORE_FILE


def _env_key_for(service: str) -> str:
    return f"{_ENV_PREFIX}{service.upper().replace('-', '_')}"


def _get_from_keyring(service: str) -> str | None:
    if keyring is None:
        return None
    try:
        return keyring.get_password(_KEYRING_SERVICE, service)
    except Exception:
        return None


def _set_in_keyring(service: str, token: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.set_password(_KEYRING_SERVICE, service, token)
        return True
    except Exception:
        return False


def _delete_from_keyring(service: str) -> None:
    if keyring is None:
        return
    try:
        keyring.delete_password(_KEYRING_SERVICE, service)
    except Exception:
        # Ignore missing records and backend-specific errors.
        return


def get_token(service: str, qakit_dir: Path) -> str | None:
    """
    Return token for service. Priority: env var > stored file.
    Env var name: QAKIT_TOKEN_<SERVICE> (upper-cased).
    """
    env_key = _env_key_for(service)
    if env_key in os.environ:
        return os.environ[env_key]
    keyring_token = _get_from_keyring(service)
    if keyring_token:
        return keyring_token
    data = load_json(_store_path(qakit_dir))
    return data.get(service)


def set_token(service: str, token: str, qakit_dir: Path) -> None:
    """Store token for service in keyring when available, else in local state."""
    if _set_in_keyring(service, token):
        # Best-effort cleanup of plaintext fallback value if it exists.
        path = _store_path(qakit_dir)
        data = load_json(path)
        if service in data:
            data.pop(service, None)
            save_json(path, data)
        return

    path = _store_path(qakit_dir)
    data = load_json(path)
    data[service] = token
    save_json(path, data)


def delete_token(service: str, qakit_dir: Path) -> None:
    """Remove stored token for service."""
    _delete_from_keyring(service)
    path = _store_path(qakit_dir)
    data = load_json(path)
    data.pop(service, None)
    save_json(path, data)
