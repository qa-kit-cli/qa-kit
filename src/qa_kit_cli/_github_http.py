"""Thin HTTPS helper for fetching remote catalogs and extension archives."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


_TIMEOUT = 15  # seconds


def fetch_text(url: str) -> str:
    """Fetch URL and return response body as text. Raises on HTTP error."""
    if not url.startswith("https://"):
        raise ValueError(f"Only HTTPS URLs are allowed, got: {url!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "qa-kit-cli/0.1"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
        return resp.read().decode("utf-8")


def fetch_json(url: str) -> Any:
    """Fetch URL and parse as JSON."""
    return json.loads(fetch_text(url))


def download_file(url: str, dest: Path) -> None:
    """Download a file from url to dest path."""
    if not url.startswith("https://"):
        raise ValueError(f"Only HTTPS URLs are allowed, got: {url!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "qa-kit-cli/0.1"})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
        dest.write_bytes(resp.read())


def safe_fetch_json(url: str, default: Any = None) -> Any:
    """Fetch JSON, returning default on any error."""
    try:
        return fetch_json(url)
    except (urllib.error.URLError, ValueError, json.JSONDecodeError):
        return default
