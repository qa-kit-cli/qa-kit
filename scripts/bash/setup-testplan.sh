#!/usr/bin/env bash
set -euo pipefail

mkdir -p .qakit/memory
cp -f templates/test-plan-template.md .qakit/memory/test-plan.md
echo "Created .qakit/memory/test-plan.md"
