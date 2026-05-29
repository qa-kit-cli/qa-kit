Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Path "tests" -Force | Out-Null
Write-Host "Initialized tests/ directory."
