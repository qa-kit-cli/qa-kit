---
command: qakit.defects
description: Summarize defects, escaped bugs, root causes, and risk trends.
---

# /qakit.defects

Summarize defects and risk trends.

Read `.qakit/memory/test-plan.md`, test results, and any defect tracking context, then generate a defect intelligence summary.

## Output format

Save to `.qakit/memory/defect-summary.md`:

```markdown
# Defect Summary

## Period: [Sprint / Release / Date range]

## Overview
| Metric | Count |
|--------|-------|
| Total defects found | 0 |
| P0 (Critical) | 0 |
| P1 (High) | 0 |
| P2 (Medium) | 0 |
| Escaped to production | 0 |
| Reopened | 0 |

## Escaped Defects (found in production)
| ID | Title | Root Cause | Missing Test Type | New Test Required |
|----|-------|------------|-------------------|-------------------|
| DEF-001 | Payment failure on mobile | Edge case in currency handling | Integration test | Yes — TC-XXX |

## Root Cause Analysis
| Root Cause Category | Count | % |
|--------------------|-------|---|
| Missing test coverage | 0 | 0% |
| Test not covering edge case | 0 | 0% |
| Environment-specific issue | 0 | 0% |
| Regression (worked before) | 0 | 0% |
| Third-party dependency | 0 | 0% |

## Trend
- Defect rate: [stable / increasing / decreasing]
- Highest risk areas: [list]
- Recommended actions: [list]

## New Tests Required
| TC ID | Scenario | Priority | Assigned To |
|-------|----------|----------|-------------|
```

## Rules

- Focus on actionable insights, not just counts.
- For each escaped defect, identify the specific missing or insufficient test.
- Recommend concrete new test cases with IDs.
- Flag recurring root causes that indicate systemic gaps.

$ARGUMENTS
