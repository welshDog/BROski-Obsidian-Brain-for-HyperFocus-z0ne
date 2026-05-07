# test_brain.ps1 — End-to-end validation of THE HYPER BRAIN v3.0
# Run with: .\test_brain.ps1

$brain = "http://localhost:8100"
$vault = "H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne\HYPERFOCUS_ZONE"

Write-Host ""
Write-Host "===== 1. HEALTH =====" -ForegroundColor Cyan
Invoke-RestMethod "$brain/health" | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "===== 2. MORNING BRIEFING (Level 13) =====" -ForegroundColor Cyan
$briefing = Invoke-RestMethod -Uri "$brain/briefing/generate" -Method Post -ContentType "application/json" -Body '{}'
$briefing | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "===== 3. VAULT — did briefing file land? =====" -ForegroundColor Cyan
$briefDir = Join-Path $vault "00-Inbox\Briefings"
if (Test-Path $briefDir) {
    Get-ChildItem $briefDir | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | Format-Table Name, LastWriteTime, Length
} else {
    Write-Host "Briefings folder does not exist yet: $briefDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===== 4. HYPERSPLIT (Level 17) =====" -ForegroundColor Cyan
$splitBody = @{
    task_title = "Get first paying student"
    task_description = "Launch Hyper-Vibe to first real user this week"
    max_depth = 3
    target_minutes_per_task = 15
} | ConvertTo-Json
$split = Invoke-RestMethod -Uri "$brain/hypersplit" -Method Post -ContentType "application/json" -Body $splitBody
$split | ConvertTo-Json -Depth 6

Write-Host ""
Write-Host "===== 5. FOCUS START (Level 16) =====" -ForegroundColor Cyan
$focusBody = @{
    intent = "Validate the brain end-to-end"
    estimated_minutes = 25
    project = "HyperBrain"
} | ConvertTo-Json
$focus = Invoke-RestMethod -Uri "$brain/focus/start" -Method Post -ContentType "application/json" -Body $focusBody
$focus | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "===== 6. FOCUS STATUS =====" -ForegroundColor Cyan
Invoke-RestMethod "$brain/focus/status" | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "===== 7. MCP STATUS (Level 15) =====" -ForegroundColor Cyan
Invoke-RestMethod "$brain/mcp/status" | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "===== DONE =====" -ForegroundColor Green
