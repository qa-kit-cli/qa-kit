"""Integration registry — imports all built-in integrations and exposes lookup helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qa_kit_cli.integrations.amp import AmpIntegration
from qa_kit_cli.integrations.auggie import AuggieIntegration
from qa_kit_cli.integrations.base import IntegrationBase
from qa_kit_cli.integrations.bob import BobIntegration
from qa_kit_cli.integrations.claude import ClaudeIntegration
from qa_kit_cli.integrations.codebuddy import CodeBuddyIntegration
from qa_kit_cli.integrations.codex import CodexIntegration
from qa_kit_cli.integrations.copilot import CopilotIntegration
from qa_kit_cli.integrations.cursor_agent import CursorAgentIntegration, CursorIntegration
from qa_kit_cli.integrations.devin import DevinIntegration
from qa_kit_cli.integrations.forge import ForgeIntegration
from qa_kit_cli.integrations.gemini import GeminiIntegration
from qa_kit_cli.integrations.generic import GenericIntegration
from qa_kit_cli.integrations.goose import GooseIntegration
from qa_kit_cli.integrations.hermes import HermesIntegration
from qa_kit_cli.integrations.iflow import IFlowIntegration
from qa_kit_cli.integrations.junie import JunieIntegration
from qa_kit_cli.integrations.kilocode import KiloCodeIntegration
from qa_kit_cli.integrations.kimi import KimiIntegration
from qa_kit_cli.integrations.kiro_cli import KiroIntegration
from qa_kit_cli.integrations.lingma import LingmaIntegration
from qa_kit_cli.integrations.opencode import OpenCodeIntegration
from qa_kit_cli.integrations.pi import PiIntegration
from qa_kit_cli.integrations.qodercli import QoderIntegration
from qa_kit_cli.integrations.qwen import QwenIntegration
from qa_kit_cli.integrations.roo import RooIntegration
from qa_kit_cli.integrations.shai import ShaiIntegration
from qa_kit_cli.integrations.tabnine import TabnineIntegration
from qa_kit_cli.integrations.trae import TraeIntegration
from qa_kit_cli.integrations.vibe import VibeIntegration
from qa_kit_cli.integrations.windsurf import WindsurfIntegration

if TYPE_CHECKING:
    pass

_REGISTRY: dict[str, type[IntegrationBase]] = {}


def _register_builtins() -> None:
    _all: list[type[IntegrationBase]] = [
        ClaudeIntegration,
        CopilotIntegration,
        GeminiIntegration,
        CursorIntegration,
        CursorAgentIntegration,
        WindsurfIntegration,
        AmpIntegration,
        CodexIntegration,
        OpenCodeIntegration,
        ForgeIntegration,
        RooIntegration,
        KiroIntegration,
        JunieIntegration,
        DevinIntegration,
        AuggieIntegration,
        TabnineIntegration,
        ShaiIntegration,
        KiloCodeIntegration,
        QwenIntegration,
        GooseIntegration,
        TraeIntegration,
        CodeBuddyIntegration,
        BobIntegration,
        KimiIntegration,
        LingmaIntegration,
        QoderIntegration,
        PiIntegration,
        IFlowIntegration,
        VibeIntegration,
        HermesIntegration,
        GenericIntegration,
    ]
    for cls in _all:
        _REGISTRY[cls.key] = cls


_register_builtins()


def list_integrations() -> list[type[IntegrationBase]]:
    """Return all registered integration classes in tier order."""
    return list(_REGISTRY.values())


def get_integration(key: str) -> type[IntegrationBase] | None:
    """Return the integration class for the given key, or None if not found."""
    return _REGISTRY.get(key)


def register_integration(cls: type[IntegrationBase]) -> None:
    """Register a third-party integration class at runtime."""
    _REGISTRY[cls.key] = cls
