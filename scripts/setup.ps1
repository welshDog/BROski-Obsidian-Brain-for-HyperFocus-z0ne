# setup.ps1 — HYPERFOCUS ZONE vault bootstrap
# Run once after cloning. BROski♾️

Write-Host "=== 🧠 HYPERFOCUS ZONE SETUP ==="  -ForegroundColor Cyan

$VAULT = "$PSScriptRoot\..\HYPERFOCUS_ZONE"

# 1. Create all folders
$folders = @(
    "00-Inbox", "00-Inbox\GitHub",
    "01-Projects", "02-Areas\Health", "02-Areas\Admin", "02-Areas\DevOps",
    "03-Resources", "04-Archive", "99-Templates", "Hub"
)
foreach ($f in $folders) {
    $path = "$VAULT\$f"
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  ✅ Created: $f" -ForegroundColor Green
    } else {
        Write-Host "  ⏭️  Exists: $f" -ForegroundColor Yellow
    }
}

# 2. Check Obsidian installed
if (Get-Command obsidian -ErrorAction SilentlyContinue) {
    Write-Host "`n✅ Obsidian found" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Install Obsidian from https://obsidian.md" -ForegroundColor Yellow
}

# 3. Check Python for sync script
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python found" -ForegroundColor Green
    pip install requests -q
    Write-Host "✅ requests installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python not found — needed for GitHub sync" -ForegroundColor Yellow
}

Write-Host "`n=== DONE BROski♾️ ==="  -ForegroundColor Cyan
Write-Host "Next: Open HYPERFOCUS_ZONE/ in Obsidian as vault." -ForegroundColor White
Write-Host "Then: Install plugins — Dataview, Templater, Calendar, Obsidian Git, Tasks" -ForegroundColor White
