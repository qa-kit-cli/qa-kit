# /qakit.ci.matrix

Design a cross-browser/platform test matrix and emit the CI config for it.

## Description

Reads the environment matrix from `.qakit/memory/test-policy.md`, then emits the CI matrix configuration (GitHub Actions `strategy.matrix` block or Jenkins parallel stages). Calculates the optimal matrix — balancing coverage against pipeline time — and recommends which tests run on which OS/browser combinations.

## Usage

```
/qakit.ci.matrix [<constraints>]
```

## Arguments

Optional `<constraints>`:
- `"chromium only for PRs"` — restrict PR matrix to one browser
- `"add Windows runner"` — include Windows in the OS dimension
- `"mobile: iOS Safari Android Chrome"` — add mobile browsers
- *(empty)* — generates from `test-policy.md` environment matrix

## Reads from memory

- `.qakit/memory/test-policy.md` — required browsers, OS variants, and which matrix gates which CI event

## Produces

CI matrix configuration snippet (GitHub Actions or Jenkins) printed inline, ready to paste into the workflow file.

Example output:
```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - os: ubuntu-latest  browser: chromium  trigger: [push, pr, release]
      - os: ubuntu-latest  browser: firefox   trigger: [push, release]
      - os: ubuntu-latest  browser: webkit    trigger: [push, release]
```

## Example

```
/qakit.ci.matrix
```

## Related commands

- `/qakit.ci.github-actions` — uses this matrix in the generated workflow
- `/qakit.policy` — update the environment matrix in `test-policy.md` before running this
