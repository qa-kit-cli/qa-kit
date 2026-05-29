"""Install slash command templates and skill files into agent-specific folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli._utils import atomic_write, ensure_dir
from qa_kit_cli.integrations import get_integration, list_integrations
from qa_kit_cli.integrations.manifest import record_files
from qa_kit_cli.presets import ActivePreset, load_active_presets


@dataclass(frozen=True)
class CommandSpec:
    command_id: str
    template_name: str
    description: str


COMMAND_MANIFEST: list[CommandSpec] = [
    # Strategy & planning
    CommandSpec("qakit.strategy", "strategy.md", "Generate QA strategy"),
    CommandSpec("qakit.testplan", "testplan.md", "Generate test plan"),
    CommandSpec("qakit.coverage", "coverage.md", "Analyze test coverage gaps"),
    CommandSpec("qakit.gaps", "gaps.md", "Find requirement/test gaps"),
    CommandSpec("qakit.policy", "policy.md", "Create or update test-policy.md"),
    CommandSpec("qakit.clarify", "clarify.md", "Resolve QA plan ambiguities"),
    CommandSpec("qakit.pyramid", "pyramid.md", "Evaluate test pyramid balance"),
    # QA lifecycle
    CommandSpec("qakit.tasks", "tasks.md", "Generate QA implementation task list"),
    CommandSpec("qakit.tasks.to-issues", "tasks.to-issues.md", "Convert QA tasks into GitHub issue drafts"),
    CommandSpec("qakit.checklist", "checklist.md", "Generate QA readiness checklist"),
    CommandSpec("qakit.traceability", "traceability.md", "Map requirements to test cases and CI jobs"),
    CommandSpec("qakit.regression", "regression.md", "Build or update regression suite"),
    CommandSpec("qakit.defects", "defects.md", "Summarize defects and risk trends"),
    CommandSpec("qakit.release-gate", "release-gate.md", "Ship/no-ship decision from coverage and risk"),
    CommandSpec("qakit.env", "env.md", "Define test environments and data rules"),
    # Test writing
    CommandSpec("qakit.write.playwright", "write.playwright.md", "Write Playwright tests"),
    CommandSpec("qakit.write.cypress", "write.cypress.md", "Write Cypress tests"),
    CommandSpec("qakit.write.selenium", "write.selenium.md", "Write Selenium tests"),
    CommandSpec("qakit.write.jest", "write.jest.md", "Write Jest tests"),
    CommandSpec("qakit.write.vitest", "write.vitest.md", "Write Vitest tests"),
    CommandSpec("qakit.write.pom", "write.pom.md", "Generate page object models"),
    CommandSpec("qakit.write.fixtures", "write.fixtures.md", "Generate fixtures and factories"),
    CommandSpec("qakit.write.a11y", "write.a11y.md", "Write accessibility tests"),
    CommandSpec("qakit.write.visual", "write.visual.md", "Write visual regression tests"),
    CommandSpec("qakit.write.api", "write.api.md", "Write API contract tests"),
    # CI
    CommandSpec("qakit.ci.github-actions", "ci.github-actions.md", "Generate GitHub Actions CI"),
    CommandSpec("qakit.ci.jenkins", "ci.jenkins.md", "Generate Jenkins pipeline"),
    CommandSpec("qakit.ci.matrix", "ci.matrix.md", "Generate test matrix"),
    CommandSpec("qakit.ci.badges", "ci.badges.md", "Generate README badges"),
    CommandSpec("qakit.ci.report", "ci.report.md", "Configure test reports"),
    # Maintenance
    CommandSpec("qakit.maintain.flaky", "maintain.flaky.md", "Diagnose flaky tests"),
    CommandSpec("qakit.maintain.refactor", "maintain.refactor.md", "Refactor test suites"),
    CommandSpec("qakit.maintain.data", "maintain.data.md", "Audit test data"),
    CommandSpec("qakit.maintain.upgrade", "maintain.upgrade.md", "Upgrade framework versions"),
    # Review
    CommandSpec("qakit.review.pr", "review.pr.md", "QA review for pull requests"),
    CommandSpec("qakit.review.bugreport", "review.bugreport.md", "Generate bug reports"),
    CommandSpec("qakit.review.accessibility", "review.accessibility.md", "Review WCAG compliance"),
]


def _apply_compositions(
    core_content: str,
    command_id: str,
    active_presets: list[ActivePreset],
) -> str:
    """Apply preset compositions in reverse priority order (priority 1 applied last → wins)."""
    result = core_content
    for preset in reversed(active_presets):
        comp = preset.get_composition(command_id)
        if comp is None:
            continue
        override = preset.read_template(str(comp.get("template", "")))
        if override is None:
            continue
        mode = str(comp.get("mode", "replace"))
        if mode == "replace":
            result = override
        elif mode == "append":
            result = result + "\n\n---\n\n" + override
    return result


class CommandRegistrar:
    """Writes slash command template files for an integration."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or get_commands_dir()

    @staticmethod
    def _apply_compositions(
        core_content: str,
        command_id: str,
        active_presets: list[ActivePreset],
    ) -> str:
        """Public static alias for module-level _apply_compositions (backward compat)."""
        return _apply_compositions(core_content, command_id, active_presets)

    def _render(
        self,
        integration_key: str,
        spec: CommandSpec,
        active_presets: list[ActivePreset] | None = None,
        resolver: "object | None" = None,
    ) -> str:
        integration = get_integration(integration_key)
        if integration is None:
            raise ValueError(f"Unknown integration: {integration_key}")

        if resolver is not None:
            resolved_path = resolver.resolve(spec.template_name)  # type: ignore[attr-defined]
            if resolved_path is None:
                raise FileNotFoundError(f"Missing template: {spec.template_name}")
            content = resolved_path.read_text(encoding="utf-8")
        else:
            source = self.templates_dir / spec.template_name
            if not source.exists():
                raise FileNotFoundError(f"Missing template: {source}")
            content = source.read_text(encoding="utf-8")

        if active_presets:
            content = _apply_compositions(content, spec.command_id, active_presets)
        return integration.render_command(spec.command_id, content, spec.description)

    def install_for_integration(
        self,
        project_root: Path,
        qakit_dir: Path,
        integration_key: str,
    ) -> list[Path]:
        from qa_kit_cli.template_resolver import TemplateResolver

        integration = get_integration(integration_key)
        if integration is None:
            raise ValueError(f"Unknown integration: {integration_key}")

        active_presets = load_active_presets(qakit_dir)
        resolver = TemplateResolver(qakit_dir, self.templates_dir)
        commands_dir = ensure_dir(integration.get_commands_dir(project_root))
        ext = integration.command_extension()
        installed: list[Path] = []

        for spec in COMMAND_MANIFEST:
            try:
                rendered = self._render(integration_key, spec, active_presets, resolver)
            except FileNotFoundError:
                continue
            filename = f"{spec.command_id}{ext}"
            target = commands_dir / filename
            atomic_write(target, rendered)
            installed.append(target)

        record_files(qakit_dir, integration_key, installed)
        return installed

    def install_all(self, project_root: Path, qakit_dir: Path) -> dict[str, list[Path]]:
        results: dict[str, list[Path]] = {}
        for integration in list_integrations():
            results[integration.key] = self.install_for_integration(project_root, qakit_dir, integration.key)
        return results


class SkillRegistrar:
    """Writes skill files for skill-capable integrations."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or get_commands_dir()

    def install_for_integration(
        self,
        project_root: Path,
        qakit_dir: Path,
        integration_key: str,
    ) -> list[Path]:
        from qa_kit_cli.template_resolver import TemplateResolver

        integration = get_integration(integration_key)
        if integration is None:
            raise ValueError(f"Unknown integration: {integration_key}")
        if not integration.supports_skills:
            raise ValueError(f"Integration '{integration_key}' does not support skills mode.")

        active_presets = load_active_presets(qakit_dir)
        resolver = TemplateResolver(qakit_dir, self.templates_dir)
        skills_base = ensure_dir(integration.get_skills_dir(project_root))
        installed: list[Path] = []

        for spec in COMMAND_MANIFEST:
            resolved_path = resolver.resolve(spec.template_name)
            if resolved_path is None:
                continue
            content = resolved_path.read_text(encoding="utf-8")
            if active_presets:
                content = _apply_compositions(content, spec.command_id, active_presets)
            rendered = integration.render_skill(spec.command_id, content, spec.description)

            skill_slug = spec.command_id.replace(".", "-")
            skill_dir = ensure_dir(skills_base / skill_slug)
            target = skill_dir / "SKILL.md"
            atomic_write(target, rendered)
            installed.append(target)

        record_files(qakit_dir, f"{integration_key}.skills", installed)
        return installed


def detect_active_integration(project_root: Path) -> str:
    """Detect active integration by existing known agent folders. Falls back to claude."""
    for integration in list_integrations():
        folder = integration.config.get("folder")
        if folder and (project_root / folder).exists():
            return integration.key
    return "claude"
