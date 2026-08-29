# Verify-BrainNote.ps1
# Verifies that notes in the HyperFocus Z0ne vault comply with the Data-to-Brain Protocol.

Write-Host "🔍 Verifying Data-to-Brain Protocol compliance..." -ForegroundColor Cyan

# Path to the HyperFocus Zone vault
$scriptDir = $PSScriptRoot
$repoRoot = (Get-Item $scriptDir).Parent.Parent
$workspaceRoot = Split-Path -Path $repoRoot -Parent
$hyperfocusZone = Join-Path $workspaceRoot "HYPERFOCUS_ZONE"

if (-not (Test-Path $hyperfocusZone)) {
    Write-Host "❌ HyperFocus Zone directory not found at: $hyperfocusZone" -ForegroundColor Red
    exit 1
}

Write-Host "Scanning vault: $hyperfocusZone" -ForegroundColor DarkGray

# Get all markdown files in the vault (recursively)
$notes = Get-ChildItem -Path $hyperfocusZone -Filter "*.md" -File -Recurse
Write-Host "Found $($notes.Count) markdown notes." -ForegroundColor DarkGray

$nonCompliant = @()
$missingTags = @()

foreach ($note in $notes) {
    try {
        $content = Get-Content -Path $note.FullName -Raw
        # Check for frontmatter
        if ($content -match '^\-\-\-\r?\n(.+?)\r?\n\-\-\-\r?\n(.*)$') {
            $frontmatter = $Matches[1]
            # Check for required tags
            $hasNotebooklmImport = $frontmatter -match 'notebooklm-import'
            $hasHfzMap = $frontmatter -match 'hfz-map'
            # We'll consider any tag that is not the two required ones as a skill tag?
            # Actually, we just need at least one more tag (the skill tag).
            # Let's extract all tags from the frontmatter line that starts with 'tags:'
            if ($frontmatter -match 'tags:\s*\[(.+)\]\r?\n') {
                $tagsLine = $Matches[1]
                # Split by comma and clean up
                $tags = $tagsLine -split ',\s*' | ForEach-Object { $_.Trim().TrimStart('#') }
                # Check if we have at least the two required ones and at least one more (skill tag)
                $required = @('notebooklm-import', 'hfz-map')
                $hasRequired = $required | ForEach-Object { $tags -contains $_ } | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
                if ($hasRequired -eq 2) {
                    # We have the two required, now check if there's at least one more tag (the skill tag)
                    if ($tags.Count -ge 3) {
                        # Note is compliant
                        continue
                    }
                }
            }
            # If we get here, the note is missing something
            $missing = @()
            if (-not $hasNotebooklmImport) { $missing += 'notebooklm-import' }
            if (-not $hasHfzMap) { $missing += 'hfz-map' }
            # For skill tag, we can't easily check without knowing what skill tags are expected.
            # We'll just note that a skill tag is missing if we don't have at least 3 tags total and we have the two required.
            if ($hasNotebooklmImport -and $hasHfzMap) {
                if ($frontmatter -match 'tags:\s*\[(.+)\]\r?\n') {
                    $tagsLine = $Matches[1]
                    $tags = $tagsLine -split ',\s*' | ForEach-Object { $_.Trim().TrimStart('#') }
                    if ($tags.Count -lt 3) {
                        $missing += 'skill tag (at least one more tag required)'
                    }
                } else {
                    $missing += 'skill tag (no tags found)'
                }
            } elseif (-not $hasNotebooklmImport -and -not $hasHfzMap) {
                $missing += 'notebooklm-import, hfz-map, and skill tag'
            } elseif (-not $hasNotebooklmImport) {
                $missing += 'notebooklm-import and skill tag'
            } elseif (-not $hasHfzMap) {
                $missing += 'hfz-map and skill tag'
            }
            $nonCompliant += @{ Path = $note.FullName; Missing = $missing -join ', ' }
        } else {
            # No frontmatter
            $nonCompliant += @{ Path = $note.FullName; Missing = 'no frontmatter' }
        }
    } catch {
        Write-Host "⚠️  Error reading $($note.FullName): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

if ($nonCompliant.Count -eq 0) {
    Write-Host ""
    Write-Host "🎉 All notes in the HyperFocus Zone vault comply with the Data-to-Brain Protocol!" -ForegroundColor Green
    Write-Host "💡 Next up is verifying session start files — starting now" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host ""
    Write-Host "🛑 Found $($nonCompliant.Count) note(s) that do not comply with the Data-to-Brain Protocol:" -ForegroundColor Red
    foreach ($entry in $nonCompliant) {
        Write-Host "   - $($entry.Path)" -ForegroundColor DarkGray
        Write-Host "     Missing: $($entry.Missing)" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "📋 Required frontmatter format:" -ForegroundColor Yellow
    Write-Host "   ---" -ForegroundColor Yellow
    Write-Host "   tags: [notebooklm-import, hfz-map, <skill-tag>]" -ForegroundColor Yellow
    Write-Host "   ---" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Please update the non-compliant notes to include the required tags." -ForegroundColor Yellow
    exit 1
}