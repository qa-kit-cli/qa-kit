---
command: qakit.review.accessibility
description: Audit a component or page for WCAG 2.1 AA compliance and provide remediation steps.
---

# /qakit.review.accessibility

Audit the specified component or page for WCAG 2.1 AA accessibility issues.

## Context

**Input:** $ARGUMENTS
*(Provide the component file path, page route, or paste the HTML/JSX to audit. Example: "src/components/Modal.tsx" or "/checkout".)*

This is a code review audit — it combines static analysis of the source code with accessibility best practice knowledge. It does not replace automated axe testing (use `/qakit.write.a11y` for that).

Read the source file at `$ARGUMENTS`. If a route is provided, read all components rendered by that route.

## WCAG 2.1 AA checklist

Work through each criterion. For each violation found, state:
- The WCAG criterion number and name
- The code location (file + line)
- The exact problem
- The fix to apply

---

### 1. Perceivable

**1.1.1 Non-text content (A)**
- All `<img>` elements have a non-empty `alt` attribute, or `alt=""` if decorative
- Icon buttons have `aria-label` or visually-hidden text
- SVGs used as content have `role="img"` and `<title>`

**1.3.1 Info and relationships (A)**
- Heading hierarchy is logical (`h1` → `h2` → `h3`, no skips)
- Lists use `<ul>`/`<ol>` not styled `<div>` rows
- Form fields are associated with `<label>` via `for`/`id`, `aria-label`, or `aria-labelledby`
- Tables have `<th scope="col/row">` headers
- Required fields are indicated with `aria-required="true"` not just `*` in label text

**1.3.5 Identify input purpose (AA)**
- Login/contact form inputs use `autocomplete` attributes (`email`, `name`, `current-password`, etc.)

**1.4.1 Use of colour (A)**
- Information is not conveyed by colour alone (error states also have an icon or text, not just red border)

**1.4.3 Contrast minimum (AA)**
- Normal text: ≥ 4.5:1 contrast ratio
- Large text (≥ 18pt or ≥ 14pt bold): ≥ 3:1
- Interactive components (button borders, input borders): ≥ 3:1

**1.4.4 Resize text (AA)**
- Content remains usable at 200% zoom without horizontal scrolling

**1.4.10 Reflow (AA)**
- Content reflows at 320px viewport without loss of functionality

### 2. Operable

**2.1.1 Keyboard (A)**
- Every interactive element is reachable and operable by keyboard alone
- No keyboard trap: pressing Tab or Escape reliably moves focus out of any component

**2.1.2 No keyboard trap (A)**
- Modals trap focus inside while open and return focus to the trigger on close
- Custom dropdowns and tooltips close on Escape

**2.4.1 Bypass blocks (A)**
- A skip-to-main-content link is the first focusable element on every page

**2.4.3 Focus order (A)**
- Tab order follows the visual and logical reading order

**2.4.7 Focus visible (AA)**
- Every focusable element has a clearly visible focus ring (not suppressed by `outline: none` without a replacement)

### 3. Understandable

**3.1.1 Language of page (A)**
- `<html lang="en">` (or correct language code) is set

**3.2.1 On focus (A)**
- No unexpected navigation or context change occurs when a component receives focus

**3.3.1 Error identification (A)**
- Form validation errors identify the specific field and describe what went wrong

**3.3.2 Labels and instructions (A)**
- Every form field has a visible label (not placeholder text only)

### 4. Robust

**4.1.1 Parsing (A)**
- No duplicate `id` attributes
- All HTML elements are properly nested

**4.1.2 Name, role, value (A)**
- Custom widgets (custom select, date picker, slider, tab panel) have correct ARIA roles, states, and properties
- `aria-expanded`, `aria-selected`, `aria-checked` are used and updated dynamically

**4.1.3 Status messages (AA)**
- Toast notifications, live regions, and status updates use `role="status"` or `aria-live="polite"`
- Error announcements use `role="alert"` or `aria-live="assertive"`

---

## Summary report

After completing the audit, produce:

### Violations found

| # | Criterion | Severity | Location | Issue | Fix |
|---|---|---|---|---|---|
| 1 | 1.3.1 | ❌ Fail | `Modal.tsx:42` | `<div class="modal-title">` not linked to modal via `aria-labelledby` | Add `aria-labelledby="modal-title-id"` to dialog element |

### Overall verdict

- **Pass** — no violations found
- **Fail** — N violations found; list P0 blockers (Criteria A violations) that must be fixed before ship
- **Warning** — advisory AA items that should be addressed

### Top 3 fixes to apply now

Ordered by impact. Provide the exact code change for each.
