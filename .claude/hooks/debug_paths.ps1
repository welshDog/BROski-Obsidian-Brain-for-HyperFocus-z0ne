# Debug script to verify path calculations

$scriptDir = $PSScriptRoot
Write-Host "Script directory: $scriptDir" -ForegroundColor DarkGray

$claudeDir = Split-Path -Path $scriptDir -Parent
$repoRoot = Split-Path -Path $claudeDir -Parent
$perCoreRoot = Split-Path -Path $repoRoot -Parent
$workspaceRoot = Split-Path -Path $perCoreRoot -Parent

Write-Host "Repository root (Obsidian Brain): $repoRoot" -ForegroundColor DarkGray
Write-Host "PerCore root: $perCoreRoot" -ForegroundColor DarkGray
Write-Host "Workspace root: $workspaceRoot" -ForegroundColor DarkGray

Write-Host "`nChecking existence:" -ForegroundColor Cyan
Write-Host "Script dir exists:  $(Test-Path $scriptDir)"
Write-Host "Claude dir exists:  $(Test-Path $claudeDir)"
Write-Host "Repo root exists:   $(Test-Path $repoRoot)"
Write-Host "PerCore root exists:$(Test-Path $perCoreRoot)"
Write-Host "Workspace root exists:$(Test-Path $workspaceRoot)"

Write-Host "`nLooking for files in workspace root:" -ForegroundColor Cyan
$wsPath = Join-Path $workspaceRoot "DASHBOARD_STATUS_*.md"
Write-Host "Looking for DASHBOARD_STATUS_*.md at: $wsPath"
Get-ChildItem -Path $workspaceRoot -Include "DASHBOARD_STATUS_*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { Write-Host "Found: $($_.FullName)" }

$wsPath = Join-Path $workspaceRoot "ECOSYSTEM_HANDOVER.md"
Write-Host "Looking for ECOSYSTEM_HANDOVER.md at: $wsPath"
if (Test-Path $wsPath) { Write-Host "Found: $wsPath" } else { Write-Host "NOT FOUND" }

$wsPath = Join-Path $workspaceRoot "PORTAL.md"
Write-Host "Looking for PORTAL.md at: $wsPath"
if (Test-Path $wsPath) { Write-Host "Found: $wsPath" } else { Write-Host "NOT FOUND" }

Write-Host "`nLooking for files in repo root (Obsidian Brain):" -ForegroundColor Cyan
$repoPath = Join-Path $repoRoot "NEXT_SESSION_HANDOVER_*.md"
Write-Host "Looking for NEXT_SESSION_HANDOVER_*.md at: $repoPath"
Get-ChildItem -Path $repoRoot -Include "NEXT_SESSION_HANDOVER_*.md" -File -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { Write-Host "Found: $($_.FullName)" }

$repoPath = Join-Path $repoRoot "CLAUDE.md"
Write-Host "Looking for CLAUDE.md at: $repoPath"
if (Test-Path $repoPath) { Write-Host "Found: $repoPath" } else { Write-Host "NOT FOUND" }

$repoPath = Join-Path $repoRoot "WHATS_DONE.md"
Write-Host "Looking for WHATS_DONE.md at: $repoPath"
if (Test-Path $repoPath) { Write-Host "Found: $repoPath" } else { Write-Host "NOT FOUND" }