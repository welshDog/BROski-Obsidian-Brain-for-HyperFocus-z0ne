# Session Start Verification Script
# Verifies required files exist and are recent (within 24 hours) before allowing work to proceed
# Missing files cause failure; outdated files cause warnings only.

Write-Host "🔍 Verifying session start files..." -ForegroundColor Cyan

# $PSScriptRoot is the directory from which the script is being run
$scriptDir = $PSScriptRoot
Write-Host "Script directory: $scriptDir" -ForegroundColor DarkGray

# Go up the directory tree to find the repository root (Obsidian Brain repo)
# hooks -> claude -> repo
$repoRoot = (Get-Item $scriptDir).Parent.Parent
# The workspace root (HperCore) is the parent of the repo root
$workspaceRoot = Split-Path -Path $repoRoot -Parent

Write-Host "Repository root (Obsidian Brain): $repoRoot" -ForegroundColor DarkGray
Write-Host "Workspace root (HperCore): $workspaceRoot" -ForegroundColor DarkGray

# Define required files and their descriptions with correct paths
$requiredFiles = @(
    # Workspace root files (first three) - located in $workspaceRoot
    @{ path = Join-Path $workspaceRoot "DASHBOARD_STATUS_*.md"; description = "LIVE blockers + proof status"; pattern = "DASHBOARD_STATUS_*" },
    @{ path = Join-Path $workspaceRoot "ECOSYSTEM_HANDOVER.md"; description = "cross-repo contracts + P0s"; pattern = "ECOSYSTEM_HANDOVER.md" },
    @{ path = Join-Path $workspaceRoot "PORTAL.md"; description = "tabs hub + jump points"; pattern = "PORTAL.md" },
    # Current repo files (last three) - located in $repoRoot (Obsidian Brain repo)
    @{ path = Join-Path $repoRoot "NEXT_SESSION_HANDOVER_*.md"; description = "session handover"; pattern = "NEXT_SESSION_HANDOVER_*" },
    @{ path = Join-Path $repoRoot "CLAUDE.md"; description = "project guidelines"; pattern = "CLAUDE.md" },
    @{ path = Join-Path $repoRoot "WHATS_DONE.md"; description = "completed work tracking"; pattern = "WHATS_DONE.md" }
)

$allGood = $true
$missing = @()
$warnings = @()
$maxAgeHours = 24  # Files should be updated within last 24 hours
$currentTime = Get-Date

foreach ($fileInfo in $requiredFiles) {
    Write-Host "Checking for $($fileInfo.path)" -ForegroundColor DarkGray
    # Find matching files
    $matchingFiles = Get-ChildItem -Path $fileInfo.path -File -ErrorAction SilentlyContinue

    if (-not $matchingFiles) {
        # Extract just the pattern part for display
        $displayPath = $fileInfo.path -split '[\\/]' | Select-Object -Last 1
        Write-Host "❌ MISSING: $($fileInfo.description) ($displayPath)" -ForegroundColor Red
        $missing += $fileInfo.description
        $allGood = $false
        continue
    }

    # Get the most recent file if multiple matches
    $latestFile = $matchingFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $fileAge = $currentTime - $latestFile.LastWriteTime

    if ($fileAge.TotalHours -gt $maxAgeHours) {
        Write-Host "⚠️  OUTDATED: $($fileInfo.description) ($($latestFile.Name)) - updated $([math]::Round($fileAge.TotalHours, 1)) hours ago" -ForegroundColor Yellow
        $warnings += "$($fileInfo.description) is outdated (updated $([math]::Round($fileAge.TotalHours, 1)) hours ago)"
    } else {
        Write-Host "✅ CURRENT: $($fileInfo.description) ($($latestFile.Name))" -ForegroundColor Green
    }
}

if (-not $allGood) {
    Write-Host ""
    Write-Host "🛑 Session start verification FAILED. Missing required files:" -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "   - $m" -ForegroundColor Red
    }
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  Warnings (outdated files):" -ForegroundColor Yellow
        foreach ($w in $warnings) {
            Write-Host "   - $w" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Host "📋 Refer to AGENT-START.md Step 1 for required files." -ForegroundColor Yellow
    Write-Host "💡 Please create the missing files before proceeding." -ForegroundColor Yellow
    # Exit with error code to prevent proceeding
    exit 1
} else {
    Write-Host ""
    if ($warnings.Count -gt 0) {
        Write-Host "⚠️  Some files are outdated (older than 24 hours):" -ForegroundColor Yellow
        foreach ($w in $warnings) {
            Write-Host "   - $w" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    Write-Host "🎉 All required files verified! Session ready to begin." -ForegroundColor Green
    Write-Host "💡 Next up is verifying session start files — starting now" -ForegroundColor Cyan
}