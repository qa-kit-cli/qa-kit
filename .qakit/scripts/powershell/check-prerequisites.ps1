Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"
Assert-Command -Name "node"
Assert-Command -Name "npm"
Assert-Command -Name "npx"

Write-Host "Prerequisite check complete."
