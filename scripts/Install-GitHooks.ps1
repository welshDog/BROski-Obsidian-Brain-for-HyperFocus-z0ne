# Install-GitHooks.ps1
# Installs the pre-commit hook (to prevent .env commits and supabase db push) in all known repos under HperCore.

Write-Host "🔧 Installing git pre-commit hooks in known repos..." -ForegroundColor Cyan

# Define the known repos relative to HperCore
$workspaceRoot = "H:\HYPERFOCUSZONE"
$perCoreRoot = Join-Path $workspaceRoot "HperCore"
$repos = @(
    "HyperCode-V2.4",
    "hyper-agents-ide",
    "Hyper-Vibe-Coding-Course",
    "HyperAgent-SDK",
    "showcase-web",
    "BROskiPets-LLM-dNFT",
    "BROski-Obsidian-Brain-for-HyperFocus-z0ne",
    "HYPER-SILLs-By-WelshDog",
    "Hyper-Docker",
    "WelshDog-Mission-Control",
    "welshdog-designs-web3-shop",
    "hyperfocuszone.com-Support-Hub",
    "HC",  # This is HperCore itself, skip?
    "trae-ide"
)

# Filter out HC and trae-ide as they are not typical repos? HC is the workspace hub.
# We'll skip HC and trae-ide for now.
$repos = $repos | Where-Object { $_ -ne "HC" -and $_ -ne "trae-ide" }

$hookContent = @'
#!/usr/bin/env bash
# pre-commit hook to prevent committing .env files and running supabase db push

# Check for .env files in the staged changes
if git diff --cached --name-only | grep -q '\.env$'; then
    echo "Error: Attempting to commit a .env file."
    echo "Secrets must stay local. Please remove the .env file from the commit."
    exit 1
fi

# Check for the string "supabase db push" in the staged changes (in any file)
if git diff --cached | grep -q 'supabase db push'; then
    echo "Error: Attempting to commit a change that contains 'supabase db push'."
    echo "Use 'supabase apply_migration' instead. Please remove the offending line."
    exit 1
fi

# If we get here, the commit is allowed.
exit 0
'@

$installed = @()
$skipped = @()
$errors = @()

foreach ($repo in $repos) {
    $repoPath = Join-Path $perCoreRoot $repo
    $hookPath = Join-Path $repoPath ".git\hooks\pre-commit"

    if (-not (Test-Path $repoPath)) {
        Write-Host "⚠️  Repo not found at $repoPath, skipping." -ForegroundColor Yellow
        $skipped += "$repo (not found)"
        continue
    }

    if (-not (Test-Path (Join-Path $repoPath ".git"))) {
        Write-Host "⚠️  $repoPath is not a git repository, skipping." -ForegroundColor Yellow
        $skipped += "$repo (not a git repo)"
        continue
    }

    # Check if hook already exists
    if (Test-Path $hookPath) {
        $existingContent = Get-Content -Path $hookPath -Raw
        if ($existingContent -like "*supabase db push*") {
            Write-Host "✅ Hook already installed in $repo` (contains supabase db push check)" -ForegroundColor Green
            $skipped += "$repo (already has hook)"
            continue
        } else {
            Write-Host "⚠️  Hook exists in $repo but does not contain our checks. Backing up and installing." -ForegroundColor Yellow
            # Backup the existing hook
            $backupPath = "$hookPath.bak_$(Get-Date -Format 'yyyyMMdd_Hmmss')"
            Copy-Item -Path $hookPath -Destination $backupPath
            Write-Host "   Backed up existing hook to $backupPath" -ForegroundColor DarkGray
        }
    }

    # Write the hook
    try {
        Set-Content -Path $hookPath -Value $hookContent -Encoding ASCII
        # Make sure it's executable (on Windows, we rely on Git Bash, but we can set the executable flag)
        # Actually, on Windows, the hook is run by Git Bash, so we don't need to set executable bit.
        # But we can do it for completeness.
        # icacls $hookPath /grant "*S-1-1-0:(X)"  # This is complex, skip for now.
        Write-Host "✅ Installed hook in $repo" -ForegroundColor Green
        $installed += $repo
    } catch {
        Write-Host ("❌ Failed to install hook in {0}: {1}" -f $repo, $_.Exception.Message) -ForegroundColor Red
        $errors += "$repo ($($_.Exception.Message))"
    }
}

Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Installed in: $($installed.Count) repo(s)" -ForegroundColor Green
if ($installed.Count -gt 0) {
    Write-Host "   - $($installed -join ', ')" -ForegroundColor DarkGray
}
Write-Host "   Skipped: $($skipped.Count) repo(s)" -ForegroundColor Yellow
if ($skipped.Count -gt 0) {
    Write-Host "   - $($skipped -join ', ')" -ForegroundColor DarkGray
}
Write-Host "   Errors: $($errors.Count) repo(s)" -ForegroundColor Red
if ($errors.Count -gt 0) {
    Write-Host "   - $($errors -join ', ')" -ForegroundColor DarkGray
}
Write-Host ""
Write-Host "💡 Next up is verifying session start files — starting now" -ForegroundColor Cyan