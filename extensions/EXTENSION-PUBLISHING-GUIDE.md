# Extension Publishing Guide

This guide covers how to distribute your extension so others can install it.

## Option 1: GitHub Release Archive

The simplest distribution method. Host a `.zip` archive as a GitHub release asset.

### Structure your archive

The `.zip` must contain `extension.yml` at any nesting level. QA Kit recursively searches for it:

```
my-extension-v0.1.0.zip
└── my-extension/
    ├── extension.yml
    ├── scripts/
    │   └── validate.py
    └── README.md
```

### Create the release

```bash
cd my-extension/
zip -r ../my-extension-v0.1.0.zip .
# Upload to GitHub Releases as an asset
```

Users install it with:

```bash
qakit extension add https://github.com/org/my-extension/releases/download/v0.1.0/my-extension-v0.1.0.zip
```

## Option 2: Community Catalog

Submit a pull request to add your extension to the community catalog at
`extensions/catalog.community.json` in the QA Kit repository.

### Catalog entry format

```json
{
  "id": "my-extension",
  "name": "My Extension",
  "version": "0.1.0",
  "description": "One-line description of what the extension does.",
  "bundled": false,
  "url": "https://github.com/org/my-extension/releases/download/v0.1.0/my-extension-v0.1.0.zip",
  "author": "Your Name",
  "homepage": "https://github.com/org/my-extension",
  "tags": ["reporting", "jira"]
}
```

### Submission checklist

- [ ] `extension.yml` validates without errors (`qakit extension add ./my-extension`)
- [ ] All hook events in `hooks` are supported (see `RFC-EXTENSION-SYSTEM.md`)
- [ ] Commands use environment variables for credentials — no hardcoded tokens
- [ ] Commands degrade gracefully when credentials are absent (print a warning, exit 0)
- [ ] README explains what each hook does and what environment variables are required
- [ ] Version follows semantic versioning

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **Patch** (`0.1.x`): Bug fixes in shell commands, no manifest changes
- **Minor** (`0.x.0`): New hooks added; backwards-compatible
- **Major** (`x.0.0`): Breaking change — removed hooks, renamed IDs

## Updating a Published Extension

1. Bump the `version` field in `extension.yml`
2. Create a new GitHub release with the updated archive
3. Update the `url` and `version` in the community catalog PR

Users upgrade installed extensions with:

```bash
qakit extension remove my-extension
qakit extension add https://github.com/org/my-extension/releases/download/v0.2.0/my-extension-v0.2.0.zip
```

## Security Requirements for Community Extensions

Community catalog submissions are reviewed for:

- No execution of downloaded code at install time
- No exfiltration of files outside the project directory
- Clear documentation of required credentials
- Commands that operate locally or call well-known APIs only

Extensions that fail these criteria will not be accepted into the community catalog.
