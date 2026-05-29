#!/usr/bin/env bash
set -euo pipefail

mkdir -p .qakit/memory
cp -f templates/qa-strategy-template.md .qakit/memory/qa-strategy.md
echo "Created .qakit/memory/qa-strategy.md"
