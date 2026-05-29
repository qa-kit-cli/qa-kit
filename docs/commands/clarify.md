# /qakit.clarify

Identify and resolve ambiguities in a QA strategy or test plan via targeted questions.

## Description

Reads the current strategy and/or test plan and identifies the `[NEEDS CLARIFICATION]` markers and any other logical gaps or unstated assumptions. Produces a list of targeted questions for the team, then — if answers are provided — updates the affected document sections.

Use this between `/qakit.strategy` and `/qakit.testplan` when the strategy contains open questions that would change the test approach if answered differently.

## Usage

```
/qakit.clarify [<answers>]
```

## Arguments

Two modes:

1. **Generate questions** (no argument):
   Reads `qa-strategy.md` and `test-plan.md` and outputs up to 5 clarification questions.

2. **Apply answers** (with argument):
   Pass the answered questions as text. Updates the affected document sections.

## Reads from memory

- `.qakit/memory/qa-strategy.md` — source of `[NEEDS CLARIFICATION]` markers
- `.qakit/memory/test-plan.md` — plan sections that depend on unresolved questions

## Produces

- *(question mode)* — a numbered list of clarification questions, printed inline
- *(answer mode)* — updates `qa-strategy.md` and/or `test-plan.md` with resolved answers

## Example

```
/qakit.clarify
```

Then, after getting answers from the team:
```
/qakit.clarify 1. Rate-limit returns 429 with Retry-After header; no session lockout. 2. Lockout is per-device, not per-account. 3. Use dedicated test OAuth tenant, not staging.
```

## Related commands

- `/qakit.strategy` — generates the strategy that this command clarifies
- `/qakit.testplan` — run after clarifying to produce the final plan
