# New-BrainNote.ps1
# A script to help follow the Data-to-Brain Protocol for importing AI explainer output.

Write-Host "🧠 Data-to-Brain Protocol Helper" -ForegroundColor Cyan
Write-Host "This script will guide you through importing AI explainer output into the HyperFocus Z0ne knowledge vault." -ForegroundColor DarkGray
Write-Host ""

# Step 0: Determine paths
$scriptDir = $PSScriptRoot
$repoRoot = (Get-Item $scriptDir).Parent.Parent
$workspaceRoot = Split-Path -Path $repoRoot -Parent
$hyperfocusZone = Join-Path $workspaceRoot "HYPERFOCUS_ZONE"

Write-Host "Workspace root: $workspaceRoot" -ForegroundColor DarkGray
Write-Host "HyperFocus Zone path: $hyperfocusZone" -ForegroundColor DarkGray

if (-not (Test-Path $hyperfocusZone)) {
    Write-Host "⚠️  Creating HyperFocus Zone directory at: $hyperfocusZone" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $hyperfocusZone -Force | Out-Null
}

# Step 1: CAPTURE
Write-Host ""
Write-Host "📝 STEP 1: CAPTURE" -ForegroundColor Green
Write-Host "Save the AI explainer output as a markdown note." -ForegroundColor DarkGray
$source = Read-Host "What is the source of this AI output? (e.g., NotebookLM, Claude, Perplexity)"
$title = Read-Host "Enter a title for the note (this will be the filename, without extension):"
# Sanitize the title for use as a filename
$safeTitle = $title -replace '[\\/:*?"<>|]', '_' -replace '\s+', ' '
if ($safeTitle -eq '') {
    Write-Host "❌ Title cannot be empty." -ForegroundColor Red
    exit 1
}
$notePath = Join-Path $hyperfocusZone ("$safeTitle.md")
if (Test-Path $notePath) {
    $overwrite = Read-Host "⚠️  A note with this title already exists. Overwrite? (y/N)"
    if ($overwrite -notmatch '^[yY]') {
        Write-Host "🛑 Operation cancelled." -ForegroundColor Red
        exit 1
    }
}
Write-Host "💡 Please paste your AI explainer content below. When finished, press Enter on an empty line:" -ForegroundColor DarkGray
$lines = @()
while ($true) {
    $line = Read-Host
    if ($line -eq '') { break }
    $lines += $line
}
$content = $lines -join "`n"
# Add a header with metadata
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$header = "---\n"
$header += "source: $source\n"
$header += "captured: $timestamp\n"
$header += "---\n\n"
$fullContent = $header + $content
# Write the file
Set-Content -Path $notePath -Value $fullContent -Encoding UTF8
Write-Host "✅ Note saved to: $notePath" -ForegroundColor Green

# Step 2: TAG
Write-Host ""
Write-Host "🏷️  STEP 2: TAG" -ForegroundColor Green
Write-Host "Add the required tags to the note." -ForegroundColor DarkGray
Write-Host "The protocol requires: #notebooklm-import #hfz-map + 1 skill tag" -ForegroundColor DarkGray
$skillTag = Read-Host "Enter a skill tag (e.g., #skill-name, #dev, #agents, etc.):"
if ($skillTag -notmatch '^#') {
    $skillTag = "#$skillTag"
}
# We'll append the tags to the end of the note, or we could insert them in the frontmatter?
# The protocol says to add tags. We'll append them as a comment or in the frontmatter.
# Let's update the frontmatter to include tags.
# Read the file again
$currentContent = Get-Content -Path $notePath -Raw
# Split into frontmatter and body
if ($currentContent -match '^\-\-\-\r?\n(.+?)\r?\n\-\-\-\r?\n(.*)$') {
    $frontmatter = $Matches[1]
    $body = $Matches[2]
    # Add tags to frontmatter
    $frontmatter += "tags: [notebooklm-import, hfz-map, $($skillTag.TrimStart('#'))]`n"
    $newContent = "---\r\n$frontmatter---\r\n$body"
} else {
    # No frontmatter, add one
    $newContent = "---\r\ntags: [notebooklm-import, hfz-map, $($skillTag.TrimStart('#'))]\r\n---\r\n$currentContent"
}
Set-Content -Path $notePath -Value $newContent -Encoding UTF8
Write-Host "✅ Tags added: notebooklm-import, hfz-map, $skillTag" -ForegroundColor Green

# Step 3: LINK
Write-Host ""
Write-Host "🔗 STEP 3: LINK" -ForegroundColor Green
Write-Host "Link back to PORTAL.md → source repo → specific file." -ForegroundColor DarkGray
$portalLink = Read-Host "Enter the link to the relevant section in PORTAL.md (or leave blank to skip):"
$sourceRepo = Read-Host "Enter the source repo (e.g., HyperCode-V2.4, BROskiPets-LLM-dNFT):"
$sourceFile = Read-Host "Enter the specific file in the source repo (e.g., README.md, RUNBOOK.md):"
if ($portalLink -or $sourceRepo -or $sourceFile) {
    $linkText = ""
    if ($portalLink) {
        $linkText += "See [PORTAL]($portalLink) for context. "
    }
    if ($sourceRepo) {
        $linkText += "Source: $sourceRepo"
        if ($sourceFile) {
            $linkText += "/$sourceFile"
        }
    }
    # Append the link to the note
    Add-Content -Path $notePath -Value "`n`n> $linkText"
    Write-Host "✅ Link added to the note." -ForegroundColor Green
} else {
    Write-Host "⚠️  No link information provided. Skipping linking step." -ForegroundColor Yellow
}

# Step 4: SPLIT
Write-Host ""
Write-Host "✂️  STEP 4: SPLIT" -ForegroundColor Green
Write-Host "Extract up to 3 micro-tasks to feed HyperSplit." -ForegroundColor DarkGray
$microTasks = @()
for ($i = 1; $i -le 3; $i++) {
    $task = Read-Host "Enter micro-task $i (or press Enter to skip):"
    if ($task -eq '') { break }
    $microTasks += $task
}
if ($microTasks.Count -gt 0) {
    Write-Host "📝 Extracted micro-tasks:" -ForegroundColor Cyan
    foreach ($task in $microTasks) {
        Write-Host "   - $task" -ForegroundColor DarkGray
    }
    # We could save these to a tasks file or just echo them for the user to act upon.
    # For now, we'll just inform the user to feed them to HyperSplit.
    Write-Host "💡 Please feed these micro-tasks to HyperSplit (e.g., via the mission director or by creating issues)." -ForegroundColor Yellow
} else {
    Write-Host "⚠️  No micro-tasks extracted." -ForegroundColor Yellow
}

# Step 5: VERIFY
Write-Host ""
Write-Host "🔍 STEP 5: VERIFY" -ForegroundColor Green
Write-Host "Confirm this is not a duplicate of live truth in the source repos." -ForegroundColor DarkGray
Write-Host "💡 Please manually check the source repo(s) for similar content to avoid duplicates." -ForegroundColor Yellow
$verified = Read-Host "Have you verified that this is not a duplicate? (y/N)"
if ($verified -match '^[yY]') {
    Write-Host "✅ Verification complete." -ForegroundColor Green
} else {
    Write-Host "⚠️  Verification skipped. Please verify before considering this note as live truth." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Data-to-Brain Protocol completed for note: $notePath" -ForegroundColor Green
Write-Host "💡 Next up is verifying session start files — starting now" -ForegroundColor Cyan