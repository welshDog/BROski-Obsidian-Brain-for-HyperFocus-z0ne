# EndSession-Handover.ps1
# Automates the creation of NEXT_SESSION_HANDOVER_*.md files at session end.

param(
    [Parameter(Mandatory=$false)]
    [switch]$NoPrompt
)

Write-Host "📝 EndSession-Handover.ps1 - Generating session handover file" -ForegroundColor Cyan

if (-not $NoPrompt) {
    $sessionEnd = Read-Host "Session end? (y/n)"
    if ($sessionEnd -notmatch '^[yY]') {
        Write-Host "🛑 Operation cancelled." -ForegroundColor Yellow
        exit 0
    }

    $includeGitLog = Read-Host "Include git log? (y/n)"
    $includeGitLog = $includeGitLog -match '^[yY]'
} else {
    $sessionEnd = 'y'
    $includeGitLog = $false
}

# Paths
$scriptDir = $PSScriptRoot
$repoRoot = (Get-Item $scriptDir).Parent.Parent
$workspaceRoot = Split-Path -Path $repoRoot -Parent

# File paths
$whatsDonePath = Join-Path $repoRoot "WHATS_DONE.md"
$claudePath = Join-Path $repoRoot "CLAUDE.md"
$portalPath = Join-Path $workspaceRoot "PORTAL.md"
$dashboardPattern = Join-Path $workspaceRoot "DASHBOARD_STATUS_*.md"
$handoverDir = $repoRoot

# Get current date for filename
$currentDate = Get-Date -Format "yyyy-MM-dd"
$handoverPath = Join-Path $handoverDir "NEXT_SESSION_HANDOVER_$currentDate.md"

# Initialize content sections
$doneSection = @()
$nextSection = @()
$blockersSection = @()
$completedSection = @()

# 1. Extract from WHATS_DONE.md (take the whole file or recent entries?)
if (Test-Path $whatsDonePath) {
    $whatsDoneContent = Get-Content -Path $whatsDonePath -Raw
    # We'll take the entire file as the "Done" section for simplicity
    $doneSection = $whatsDoneContent -split "`r?`n"
} else {
    $doneSection = @("WHATS_DONE.md not found.")
}

# 2. Extract TODOs from CLAUDE.md and DASHBOARD_STATUS_*.md
function Get-TodosFromFile([string]$path) {
    if (-not (Test-Path $path)) { return @() }
    $content = Get-Content -Path $path
    # Look for lines that start with "- [ ]" or contain "TODO" or "OPEN ACTIONS"
    $todos = $content | Where-Object { $_ -match '^\s*-\s*\[\s*\]' -or $_ -match 'TODO' -or $_ -match 'OPEN ACTIONS' -or $_ -match '🔴' -or $_ -match '🟡' }
    return $todos
}

$claudeTodos = Get-TodosFromFile $claudePath
$dashboardFiles = Get-ChildItem -Path $dashboardPattern -File -ErrorAction SilentlyContinue
$dashboardTodos = @()
foreach ($file in $dashboardFiles) {
    $dashboardTodos += Get-TodosFromFile $file.FullName
}
$portalTodos = Get-TodosFromFile $portalPath

# Combine and deduplicate (simple approach)
$allTodos = ($claudeTodos + $dashboardTodos + $portalTodos) | Select-Object -Unique
$nextSection = $allTodos

# 3. Blockers: we can look for 🔴 in the same files
function Get-BlockersFromFile([string]$path) {
    if (-not (Test-Path $path)) { return @() }
    $content = Get-Content -Path $path
    $blockers = $content | Where-Object { $_ -match '🔴' }
    return $blockers
}

$claudeBlockers = Get-BlockersFromFile $claudePath
$dashboardBlockers = @()
foreach ($file in $dashboardFiles) {
    $dashboardBlockers += Get-BlockersFromFile $file.FullName
}
$portalBlockers = Get-BlockersFromFile $portalPath
$blockersSection = ($claudeBlockers + $dashboardBlockers + $portalBlockers) | Select-Object -Unique

# 4. Completed: we can look for 🟢 or completed checkboxes? For now, we'll leave empty or take from WHATS_DONE?
# We'll leave the completed section empty for now, or we can take the last entry from WHATS_DONE?
# For simplicity, we'll skip the completed section in the generated file and let the user fill it.

# 5. Git log
$gitLogSection = @()
if ($includeGitLog) {
    try {
        $gitLog = git log --oneline -10
        $gitLogSection = @("## 📜 Recent Git Log (last 10 commits)") + $gitLog -split "`r?`n"
    } catch {
        $gitLogSection = @("## 📜 Recent Git Log", "Error retrieving git log: $($_.Exception.Message)")
    }
}

# Build the handover content
$handoverContent = @(
    "# NEXT_SESSION_HANDOVER_$currentDate",
    "",
    "## 🚀 Next Session Tasks",
    "",
    "- [ ] Verify session start files (completed via hook)",
    "",
    "## 📝 Notes",
    "",
    "This handover file was generated automatically by EndSession-Handover.ps1.",
    "Please update with actual tasks for the next session.",
    "",
    "## 🔴 Blockers",
    ""
)

if ($blockersSection.Count -gt 0) {
    $handoverContent += $blockersSection
} else {
    $handoverContent += "- None at the moment."
}

$handoverContent += ""
$handoverContent += "## 🟡 Pending"
$handoverContent += ""
if ($nextSection.Count -gt 0) {
    $handoverContent += $nextSection
} else {
    $handoverContent += "- No pending items."
}

$handoverContent += ""
$handoverContent += "## 🟢 Completed"
$handoverContent += ""
if ($doneSection.Count -gt 0) {
    # We'll add a few lines from WHATS_DONE? For now, we'll note that it's generated.
    $handoverContent += "- Handover file generated automatically."
    $handoverContent += "- See WHATS_DONE.md for completed work."
} else {
    $handoverContent += "- No completed items recorded."
}

$handoverContent += ""
$handoverContent += "## 📋 References"
$handoverContent += ""
$handoverContent += "- [DASHBOARD_STATUS_*.md]($dashboardPattern) — LIVE blockers + proof status"
$handoverContent += "- [ECOSYSTEM_HANDOVER.md]($($workspaceRoot)\ECOSYSTEM_HANDOVER.md) — cross-repo contracts + P0s"
$handoverContent += "- [PORTAL.md]($portalPath) — tabs hub + jump points"
$handoverContent += "- [CLAUDE.md]($claudePath) — project guidelines"
$handoverContent += "- [WHATS_DONE.md]($whatsDonePath) — completed work tracking"

if ($includeGitLog) {
    $handoverContent += ""
    $handoverContent += $gitLogSection
}

$handoverContent += ""
$handoverContent += ""
$handoverContent += '> 🐶♾️ Built by @welshDog · Llanelli, Wales · *"Stop apologising for your brain. Start building."*'

# Write the file
Set-Content -Path $handoverPath -Value ($handoverContent -join "`r`n") -Encoding UTF8

Write-Host ""
Write-Host "✅ Handover file generated: $handoverPath" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next up is verifying session start files — starting now" -ForegroundColor Cyan