Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Path ".qakit/memory" -Force | Out-Null
Copy-Item -LiteralPath "templates/qa-strategy-template.md" -Destination ".qakit/memory/qa-strategy.md" -Force

Write-Host "Created .qakit/memory/qa-strategy.md"
