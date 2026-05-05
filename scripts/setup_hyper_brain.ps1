# HYPER BRAIN v3.0 — Bootstrap Setup Script
# Run from vault root: .\scripts\setup_hyper_brain.ps1

Write-Host "🧠 HYPER BRAIN v3.0 Setup Starting..." -ForegroundColor Cyan

# Create required vault directories
$dirs = @(
    "HYPERFOCUS_ZONE\Hub",
    "HYPERFOCUS_ZONE\Analytics",
    "HYPERFOCUS_ZONE\Tasks",
    "HYPERFOCUS_ZONE\Snapshots",
    "HYPERFOCUS_ZONE\Briefings",
    "HYPERFOCUS_ZONE\GitHub",
    "HYPERFOCUS_ZONE\99-Templates",
    ".obsidian\snippets"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ⏭️  Exists: $dir" -ForegroundColor Gray
    }
}

# Check Docker
Write-Host ""`n🐳 Checking Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Docker not found — install Docker Desktop first!" -ForegroundColor Red
    exit 1
}

# Check if docker folder exists
if (-not (Test-Path ".\docker\docker-compose.hyper-brain.yml")) {
    Write-Host "  ⚠️  docker-compose.hyper-brain.yml not found in .\docker\" -ForegroundColor Yellow
    Write-Host "      Add the docker files first, then rerun setup." -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Docker compose file found" -ForegroundColor Green
}

# Create .env for hyper-brain if missing
if (-not (Test-Path ".env.hyper-brain")) {
    $envContent = @"
VAULT_PATH=.
LLM_BASE_URL=http://localhost:11434
LMSTUDIO_URL=http://localhost:1234
LLM_MODEL=llama3
GITHUB_WEBHOOK_SECRET=
HYPER_BRAIN_PORT=8100
"@
    $envContent | Out-File ".env.hyper-brain" -Encoding UTF8
    Write-Host "  ✅ Created: .env.hyper-brain (fill in your secrets!)" -ForegroundColor Green
} else {
    Write-Host "  ⏭️  .env.hyper-brain already exists" -ForegroundColor Gray
}

Write-Host ""`n🚀 Quick Deploy Commands:" -ForegroundColor Cyan
Write-Host "  docker compose -f docker\docker-compose.hyper-brain.yml up -d" -ForegroundColor White
Write-Host "  Invoke-RestMethod http://localhost:8100/health" -ForegroundColor White

Write-Host ""`n✅ Setup complete! HYPER BRAIN v3.0 ready to launch. LET'S GO BROski♾️!" -ForegroundColor Green
