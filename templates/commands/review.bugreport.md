---
command: qakit.review.bugreport
description: Generate a structured bug report with repro steps, severity, and Jira-ready formatting.
---

# /qakit.review.bugreport

Generate a complete, structured bug report.

## Context

**Input:** $ARGUMENTS
*(Describe the bug. Include: what you did, what you expected, what actually happened. Paste any error messages, stack traces, or screenshots.)*

Before writing, read:
- `.qakit/memory/test-policy.md` — Defect Severity Taxonomy (P0–P3 definitions) and SLA

## Bug report

Generate the report in the following format. Every field is mandatory — infer what you can from `$ARGUMENTS` and mark anything that requires human confirmation with `[TO CONFIRM]`.

---

**ID:** BUG-[auto — leave blank for Jira to assign]
**Date:** [today's date]
**Reporter:** [name or team]
**Status:** Open

---

### Summary

One sentence: `<Component>` does `<unexpected behaviour>` when `<condition>`.

### Severity

Assign using the taxonomy from `test-policy.md`:
- **P0 — Critical** — data loss, auth bypass, payments broken, app unlaunchable
- **P1 — High** — primary user journey broken, major data corruption
- **P2 — Medium** — secondary journey degraded, workaround exists
- **P3 — Low** — cosmetic, minor UX

**Severity:** P[N] — [one-line justification]

### Priority

Separate from severity. Priority is business urgency:
- **Critical** — must be fixed before current sprint ships
- **High** — fix in this sprint
- **Medium** — fix next sprint
- **Low** — backlog

**Priority:** [Critical / High / Medium / Low]

### Environment

| Field | Value |
|---|---|
| Application version | |
| Browser / client | |
| OS | |
| Test environment | staging / production / local |
| Date / time of occurrence | |

### Steps to reproduce

Numbered, precise, atomic steps. Each step is a single action:

1. Navigate to `/checkout`
2. Add product "Widget Pro" to cart
3. Click "Proceed to checkout"
4. Enter card number `4000 0000 0000 0002` (decline test card)
5. Click "Place order"

**Minimum reproducible scenario:** [simplify to the fewest steps that still trigger the bug]

### Expected result

What should happen after Step N: `…`

### Actual result

What actually happens: `…`

Include:
- Exact error message (copy-paste, not paraphrase)
- HTTP status code if a network request is involved
- Console errors (from browser DevTools)

### Evidence

- [ ] Screenshot: [attach]
- [ ] Screen recording: [attach]
- [ ] HAR file: [attach if network issue]
- [ ] Console log: [paste]
- [ ] Stack trace: [paste]
- [ ] Linked test: TC-NNN [link if a test already covers this scenario]

### Reproducibility

- [ ] Reproducible every time
- [ ] Intermittent — reproduces X out of Y attempts
- [ ] Reproduced once, cannot reliably reproduce

### Root cause hypothesis

Based on the symptoms, the likely cause is:
`[hypothesis — e.g., "the frontend sends the card object before the billing address is validated, so the API rejects the order with a 422 but the UI shows a generic error instead of a field-level message"]`

**Confidence:** High / Medium / Low

### Suggested fix

`[Specific suggestion if known — e.g., "in PaymentForm.tsx, move the submitOrder() call inside the onBillingAddressValid callback, not the onSubmit handler"]`

### Related

- Jira ticket: [link if exists]
- PR: [link if a recent change introduced this]
- Related TC IDs: TC-NNN, TC-NNN

---

After generating the report, print the Jira-formatted summary line:
`[P{N}][BUG] <Component>: <one-line summary>`