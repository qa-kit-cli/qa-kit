# QA-Kit-Driven Testing

QA-Kit-Driven Testing is a workflow where testing intent is authored and reviewed as a first-class artifact before implementation details are finalized.
Instead of treating tests as cleanup work at the end of delivery, QA artifacts are versioned, discussed, traced, and gated exactly like production code.

## 1) What Is QA-Kit-Driven Testing

### Core Philosophy
- Strategy is a deliverable, not a note.
- Risk drives test depth.
- Traceability is explicit.
- Release quality is decided by evidence, not optimism.

### Why This Exists
Many teams have strong feature delivery workflows but inconsistent test workflows.
Symptoms include flaky suites, weak coverage on risky components, missing non-functional testing, and releases gated by confidence rather than data.
QA-Kit addresses this by making quality planning and quality execution systematic.

### First-Class QA Artifacts
QA-Kit emphasizes persistent, reviewable artifacts:
- `test-policy.md` for team rules and thresholds
- `qa-strategy.md` for risk model and investment focus
- `test-plan.md` for executable scope and prioritization
- `traceability-matrix.md` for requirement-to-test linkage
- `release-gate.md` for ship/no-ship evidence

### Command Examples
- `/qakit.policy`
- `/qakit.strategy`
- `/qakit.testplan`
- `/qakit.tasks`
- `/qakit.traceability`
- `/qakit.release-gate`

### Before/After Comparison
Before: tests are written after coding is complete, coverage is measured once, and release risk is discussed ad hoc.
After: risk is modeled up front, test work is planned explicitly, coverage and defect trends are tracked continuously, and release decisions are objective.

## 2) The QA Lifecycle (9 Phases)

### Phase 1: policy
Purpose: Define quality rules, ownership, and minimum standards.
Primary Commands: /qakit.policy
Expected Outputs: test-policy.md, coverage thresholds, flaky handling policy
Definition of Done: Policy accepted by engineering + QA leads.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.policy with repository context and current constraints.

### Phase 2: strategy
Purpose: Map product risk to quality investment priorities.
Primary Commands: /qakit.strategy
Expected Outputs: qa-strategy.md, risk tiers, focus areas
Definition of Done: High-risk areas have clear test intent.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.strategy with repository context and current constraints.

### Phase 3: testplan
Purpose: Convert strategy to executable, prioritized test scope.
Primary Commands: /qakit.testplan
Expected Outputs: test-plan.md, test IDs, entry/exit criteria
Definition of Done: Plan includes scope, out-of-scope, and environments.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.testplan with repository context and current constraints.

### Phase 4: tasks
Purpose: Turn plan into implementation-ready work items.
Primary Commands: /qakit.tasks, /qakit.tasks.issues
Expected Outputs: backlog tickets, acceptance criteria, owners
Definition of Done: Tasks are estimable and dependency-aware.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.tasks with repository context and current constraints.

### Phase 5: write
Purpose: Author and organize tests for target layers.
Primary Commands: /qakit.write.playwright, /qakit.write.jest, /qakit.write.api
Expected Outputs: test code, fixtures, data setup, selectors
Definition of Done: Tests are deterministic and maintainable.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.write.playwright with repository context and current constraints.

### Phase 6: ci
Purpose: Automate test execution with actionable feedback loops.
Primary Commands: /qakit.ci.github-actions, /qakit.ci.matrix, /qakit.ci.report
Expected Outputs: pipelines, matrix jobs, reports, badges
Definition of Done: PR feedback is fast and stable.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.ci.github-actions with repository context and current constraints.

### Phase 7: traceability
Purpose: Prove requirements are covered and auditable.
Primary Commands: /qakit.traceability
Expected Outputs: traceability matrix, uncovered item list
Definition of Done: Each requirement maps to tests and CI jobs.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.traceability with repository context and current constraints.

### Phase 8: regression
Purpose: Protect critical behavior over time.
Primary Commands: /qakit.regression, /qakit.maintain.flaky
Expected Outputs: regression suite definition, quarantine policy
Definition of Done: High-value tests are fast and trustworthy.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.regression with repository context and current constraints.

### Phase 9: release-gate
Purpose: Make an explicit ship/no-ship decision from evidence.
Primary Commands: /qakit.release-gate, /qakit.defects
Expected Outputs: release gate report, risk acceptance log
Definition of Done: Decision and rationale are documented.

Execution Notes:
- Keep artifacts short but concrete.
- Link every claim to measurable evidence.
- Record assumptions explicitly.
- Capture known gaps and follow-up owners.

Quality Smells to Watch:
- Vague goals without coverage targets.
- Tests that pass locally but fail under CI variance.
- Requirements that have no mapped validation path.
- Release notes that do not mention residual risk.

Example Prompt:
//qakit.release-gate with repository context and current constraints.

## 3) When To Use qa-kit

### Greenfield Projects
- Establish quality standards before architecture ossifies.
- Prevent accidental testing blind spots during rapid iteration.

### Existing Codebases Without Coherent Tests
- Build risk-aware test plans instead of chasing raw coverage percentages.
- Introduce traceability without rewriting all tests at once.

### CI/CD Migrations
- Define matrix strategy deliberately (OS, Python versions, browsers, DB variants).
- Standardize reporting and gating signals before rollout.

### Compliance-Driven Testing
- Map policy controls to executable tests and retention evidence.
- Preserve auditable linkages across requirements, tests, and releases.

### Team-Scaling Moments
- New hires can onboard through explicit QA artifacts.
- Multi-team programs can compare quality posture using shared templates.

## 4) qa-kit vs spec-kit

spec-kit and qa-kit are complementary, not competing.

### Responsibility Split
- spec-kit: feature lifecycle (problem framing, product intent, implementation rollout).
- qa-kit: test lifecycle (risk model, validation strategy, release quality decisions).

### Practical Integration Pattern
1. Use spec-kit to define what is being built and why.
2. Use qa-kit to define how correctness, reliability, and risk will be proven.
3. Keep both artifacts linked in pull requests and release notes.

### Before/After Example A
Before: feature spec approved, QA starts after implementation merge.
After: feature spec and QA strategy are reviewed together before execution.

### Before/After Example B
Before: acceptance criteria are narrative only.
After: acceptance criteria map to test IDs and CI evidence.

### Before/After Example C
Before: release confidence is informal.
After: release confidence is tied to a release-gate artifact.

## 5) Test Pyramid Philosophy

The `qakit.pyramid` command helps teams evaluate whether test investment matches risk and feedback-speed goals.

### Recommended Default Ratios
- Unit: 65-75%
- Service/API: 15-25%
- UI/E2E: 5-15%
- Exploratory and non-functional depth is additional, risk-driven work.

### Why Ratios Matter
- Too much UI/E2E coverage causes slow and flaky pipelines.
- Too little API coverage hides integration failures until late stages.
- Missing unit depth increases bug-fix cycle time.

### Pyramid Evaluation Questions
- Are high-risk behaviors tested at more than one layer?
- Is each PR validated in under an acceptable cycle time?
- Are failures diagnosable from logs and artifacts alone?
- Is flaky test debt tracked with owners and deadlines?

### Commands for Pyramid Work
- `/qakit.pyramid` to assess current balance.
- `/qakit.coverage` to identify missing depth by component.
- `/qakit.maintain.flaky` to isolate brittle checks.

### Before/After Comparison
Before: 40-minute pipelines blocked by UI flakes.
After: most checks complete quickly in lower layers, UI tests focus on critical journeys.

## 6) Release Gate Philosophy

A release gate is a decision framework, not a ritual.
The output should tell stakeholders exactly why a build is shippable or blocked.

### Ship Decision Inputs
- Requirement coverage status
- Open defect severity distribution
- Recent regression trend
- Flaky test volume and impact
- Security and compliance checks
- Performance/error-budget posture

### No-Ship Triggers (Typical)
- Unmitigated P0/P1 defects in release scope
- Required requirement traces missing
- Critical pipeline stage instability
- Failing contract tests for externally consumed APIs
- Compliance controls lacking evidence

### Conditional Ship Scenarios
- Known medium-risk defects with approved business acceptance
- Controlled rollout and active monitoring plan
- Hotfix and rollback paths tested and staffed

### Commands for Gate Preparation
- `/qakit.defects` for risk summaries
- `/qakit.traceability` for proof of requirement coverage
- `/qakit.regression` for critical-path protection status
- `/qakit.release-gate` for final decision artifact

### Suggested Gate Output Template
1. Scope of release
2. Quality evidence summary
3. Residual risk list
4. Decision: Ship / No Ship / Conditional Ship
5. Approvers and timestamp

## 7) End-to-End Example Workflow

1. `/qakit.policy` creates baseline rules.
2. `/qakit.strategy` ranks payment and authentication as highest risk.
3. `/qakit.testplan` adds TC IDs and layered coverage goals.
4. `/qakit.tasks` produces sprint-ready QA tasks.
5. `/qakit.write.api` and `/qakit.write.playwright` generate tests.
6. `/qakit.ci.github-actions` and `/qakit.ci.matrix` wire CI jobs.
7. `/qakit.traceability` finds one missing requirement path.
8. `/qakit.regression` updates smoke/regression sets.
9. `/qakit.release-gate` documents a conditional ship with rollback plan.

## 8) Practical Operating Rules

- Keep command outputs committed to git.
- Review QA artifacts in pull requests, not after merge.
- Avoid vanity metrics; tie metrics to risk.
- Prefer deterministic tests over broad but flaky suites.
- Quarantine flakes with owner and deadline, never indefinitely.
- Revisit policy and strategy every release cycle.

## 9) Common Anti-Patterns

- Writing test plans that no one executes.
- Treating end-to-end tests as primary correctness proof.
- Measuring success only by line coverage.
- Ignoring defect leakage trends across releases.
- Shipping with undocumented risk acceptance.

## 10) Command Cheat Sheet

- /qakit.policy - define quality governance
- /qakit.strategy - establish risk-based test approach
- /qakit.testplan - create test scope and ID map
- /qakit.gaps - detect uncovered requirements
- /qakit.tasks - break QA plan into work
- /qakit.write.playwright - author browser tests
- /qakit.write.jest - author unit/integration tests
- /qakit.write.api - author API contract tests
- /qakit.ci.github-actions - scaffold CI workflow
- /qakit.ci.matrix - design environment matrix
- /qakit.ci.report - standardize report outputs
- /qakit.traceability - map requirements to evidence
- /qakit.regression - maintain regression scope
- /qakit.maintain.flaky - investigate flaky tests
- /qakit.defects - summarize defect posture
- /qakit.release-gate - produce ship/no-ship report

## 11) Appendix: Detailed Checklists

Checklist Item 1: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 2: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 3: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 4: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 5: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 6: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 7: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 8: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 9: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 10: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 11: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 12: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 13: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 14: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 15: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 16: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 17: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 18: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 19: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 20: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 21: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 22: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 23: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 24: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 25: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 26: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 27: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 28: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 29: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 30: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 31: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 32: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 33: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 34: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 35: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 36: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 37: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 38: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 39: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 40: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 41: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 42: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 43: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 44: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 45: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 46: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 47: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 48: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 49: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 50: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 51: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 52: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 53: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 54: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 55: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 56: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 57: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 58: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 59: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 60: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 61: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 62: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 63: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 64: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 65: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 66: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 67: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 68: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 69: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 70: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 71: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 72: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 73: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 74: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 75: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 76: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 77: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 78: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 79: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 80: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 81: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 82: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 83: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 84: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 85: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 86: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 87: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 88: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 89: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 90: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 91: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 92: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 93: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 94: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 95: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 96: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 97: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 98: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 99: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 100: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 101: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 102: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 103: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 104: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 105: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 106: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 107: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 108: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 109: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 110: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 111: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 112: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 113: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 114: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 115: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 116: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 117: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 118: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 119: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
Checklist Item 120: Confirm artifact linkage, owner, due date, and measurable acceptance condition.
