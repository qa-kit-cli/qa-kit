Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Path ".qakit/memory" -Force | Out-Null
Copy-Item -LiteralPath "templates/test-plan-template.md" -Destination ".qakit/memory/test-plan.md" -Force

Write-Host "Created .qakit/memory/test-plan.md"
