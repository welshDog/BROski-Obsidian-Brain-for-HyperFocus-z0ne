# BROski-Brain-Quick-Start.ps1
# One script to boot the entire BROski Brain + register PSAI tools
# Usage: .\BROski-Brain-Quick-Start.ps1

$BrainRoot = $PSScriptRoot

Write-Host "`nBROski Brain -- Quick Start" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host "Root: $BrainRoot`n" -ForegroundColor Gray

# 1. Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor White
try {
    $pyVer = python --version 2>&1
    Write-Host "  OK: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Python not found. Install from python.org" -ForegroundColor Red
    exit 1
}

# 2. Install Python deps
Write-Host "`n[2/5] Installing Python requirements..." -ForegroundColor White
pip install -r "$BrainRoot\requirements.txt" -q
Write-Host "  OK" -ForegroundColor Green

# 3. Check PSAI module
Write-Host "`n[3/5] Checking PSAI module..." -ForegroundColor White
if (-not (Get-Module -ListAvailable -Name PSAI)) {
    Write-Host "  Installing PSAI..." -ForegroundColor Yellow
    Install-Module PSAI -Scope CurrentUser -Force
}
Write-Host "  OK: PSAI ready" -ForegroundColor Green

# 4. Start MCP bridge in background
Write-Host "`n[4/5] Starting MCP bridge (mcp_bridge.py)..." -ForegroundColor White
$mcpJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    python "$root\mcp_bridge.py"
} -ArgumentList $BrainRoot
Start-Sleep -Seconds 2
try {
    Invoke-RestMethod -Uri "http://localhost:8823/health" -TimeoutSec 3 | Out-Null
    Write-Host "  OK: MCP bridge running at :8823" -ForegroundColor Green
} catch {
    Write-Host "  Warn: MCP bridge not yet responding (may still be starting)" -ForegroundColor Yellow
}

# 5. Register PSAI tools
Write-Host "`n[5/5] Registering PSAI tools..." -ForegroundColor White
Import-Module PSAI -ErrorAction SilentlyContinue
$tools = . "$BrainRoot\PSAI-Register-Tools.ps1"
Write-Host "  OK: $($tools.Count) tools registered" -ForegroundColor Green

# Done!
Write-Host "`nBROski Brain is LIVE!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor Cyan
Write-Host "  python morning_briefing_ai.py   -- start your day" -ForegroundColor White
Write-Host "  python session_snapshot.py      -- save your session" -ForegroundColor White
Write-Host "  python focus_tracker.py         -- check focus state" -ForegroundColor White
Write-Host "  aish                            -- launch AI Shell with brain connected" -ForegroundColor White
Write-Host ""
Write-Host "aish MCP config: copy aish-mcp-config.json to `$env:APPDATA\AIShell\mcp-servers.json" -ForegroundColor Gray
Write-Host ""
