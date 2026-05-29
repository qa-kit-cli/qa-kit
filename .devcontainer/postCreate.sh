#!/usr/bin/env bash
set -euo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

uv pip install -e ".[dev,test]" --system

npx playwright install --with-deps chromium 2>/dev/null || true

python -m pytest tests/ -q --tb=short -x

echo ""
echo "QA Kit dev environment ready. Run: qakit --help"
