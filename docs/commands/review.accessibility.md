# /qakit.review.accessibility

Audit a component or page for WCAG 2.1 AA compliance criteria.

## Description

Performs a manual + automated WCAG 2.1 AA compliance review of the specified component or page. Checks keyboard navigation, focus management, colour contrast, ARIA roles and labels, screen reader announcements, and form error handling. Produces a prioritised list of violations and remediation guidance.

Complements `/qakit.write.a11y` (which writes automated axe-core tests) by covering criteria that automated tools cannot detect — cognitive load, logical reading order, meaningful link text, and motion sensitivity.

## Usage

```
/qakit.review.accessibility <page or component>
```

## Arguments

- Page route, component name, or source file path
- Examples: `"login page"`, `src/components/Modal.tsx`, `"/checkout/payment"`

## Reads from memory

- `.qakit/memory/test-policy.md` — required WCAG level (AA), which pages are in scope

## Produces

Inline accessibility audit report with sections:
- **Keyboard navigation** — tab order, focus indicators, keyboard traps
- **Screen reader** — ARIA labels, live regions, semantic HTML
- **Colour and contrast** — contrast ratio checks for text and interactive elements
- **Forms** — error identification, label association, required field marking
- **Motion and animation** — `prefers-reduced-motion` compliance
- **Remediation checklist** — prioritised by severity (blocker / major / minor)

## Example

```
/qakit.review.accessibility login page
```

## Related commands

- `/qakit.write.a11y` — write automated axe-core tests for the audited page
- `/qakit.review.pr` — include accessibility compliance in a PR QA review
