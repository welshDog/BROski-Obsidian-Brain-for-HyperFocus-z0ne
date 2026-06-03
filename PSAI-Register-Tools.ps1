# PSAI-Register-Tools.ps1
# Registers BROski-Brain Python tools as PSAI agent-callable functions
# Run AFTER: Install-Module PSAI
# Usage: Import-Module PSAI; .\PSAI-Register-Tools.ps1

$BrainRoot = $PSScriptRoot

function Invoke-BrainPython {
    param([string]$Script, [hashtable]$Args = @{})
    $argStr = ($Args.GetEnumerator() | ForEach-Object { "--$($_.Key) '$($_.Value)'" }) -join " "
    $cmd = "python `"$BrainRoot\$Script`" $argStr"
    return Invoke-Expression $cmd
}

$BROskiBrainTools = @(
    @{
        name        = "run_morning_briefing"
        description = "Runs the BROski AI morning briefing. Summarises focus sessions, project status, and today's priorities. Best tool to call at session start."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "morning_briefing_ai.py" }
    },
    @{
        name        = "get_focus_tracker"
        description = "Returns current focus session data — active sessions, duration, energy level, project context."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "focus_tracker.py" }
    },
    @{
        name        = "run_analytics"
        description = "Runs the BROski analytics engine. Returns productivity stats, focus heatmap data, streaks and patterns."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "analytics_engine.py" }
    },
    @{
        name        = "save_session_snapshot"
        description = "Saves the current session state to the Obsidian vault as a timestamped snapshot. Call at end of every session."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "session_snapshot.py" }
    },
    @{
        name        = "build_constellation"
        description = "Rebuilds the BROski knowledge graph from Obsidian vault notes. Links projects, sessions and ideas."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "constellation_builder.py" }
    },
    @{
        name        = "run_distraction_filter"
        description = "Runs the AI distraction filter. Checks active processes and browser tabs against current focus goal."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "ai_distraction_filter.py" }
    },
    @{
        name        = "query_brain_core"
        description = "Queries the hyper_brain_core directly. Use for knowledge retrieval, context lookup, and session history."
        parameters  = @{ query = "string" }
        function    = { param($p) Invoke-BrainPython -Script "hyper_brain_core.py" -Args @{ query = $p.query } }
    },
    @{
        name        = "get_events_feed"
        description = "Returns latest events from the BROski events feed — task completions, XP awards, alerts."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "events_feed.py" }
    },
    @{
        name        = "get_gamification_summary"
        description = "Returns BROski gamification stats — XP totals, level, streaks, badges, BROski tokens earned."
        parameters  = @{}
        function    = { Invoke-BrainPython -Script "gamification_summary.py" }
    },
    @{
        name        = "run_brain_health_check"
        description = "Runs a full BROski Brain health check — all Python tools, MCP bridge, Obsidian vault, Docker containers."
        parameters  = @{}
        function    = {
            Write-Host "`nBROski Brain Health Check -- $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
            $tools = @(
                "hyper_brain_core.py",
                "focus_tracker.py",
                "analytics_engine.py",
                "morning_briefing_ai.py",
                "mcp_bridge.py",
                "session_snapshot.py",
                "constellation_builder.py",
                "ai_distraction_filter.py"
            )
            foreach ($t in $tools) {
                $path = Join-Path $BrainRoot $t
                $status = if (Test-Path $path) { "OK" } else { "MISSING" }
                $color  = if ($status -eq "OK") { "Green" } else { "Red" }
                Write-Host "  [$status] $t" -ForegroundColor $color
            }

            Write-Host "`nMCP Bridge:" -ForegroundColor White
            try {
                $r = Invoke-RestMethod -Uri "http://localhost:8823/health" -TimeoutSec 3
                Write-Host "  OK: $($r | ConvertTo-Json -Compress)" -ForegroundColor Green
            } catch {
                Write-Host "  Not running (start mcp_bridge.py first)" -ForegroundColor Yellow
            }

            Write-Host "`nObsidian Vault:" -ForegroundColor White
            $vaultDirs = @("HYPERFOCUS_ZONE", "HYPER-SILLs", "sessions", "Ops-Logs")
            foreach ($d in $vaultDirs) {
                $exists = Test-Path (Join-Path $BrainRoot $d)
                $color  = if ($exists) { "Green" } else { "Yellow" }
                Write-Host "  $(if ($exists) { 'OK' } else { 'Missing' }): $d" -ForegroundColor $color
            }
            Write-Host "`nBrain health check complete.`n" -ForegroundColor Yellow
        }
    }
)

Write-Host "`nPSAI Tool Registration -- BROski Brain" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
foreach ($tool in $BROskiBrainTools) {
    Write-Host "  Registered: $($tool.name)" -ForegroundColor Green
}
Write-Host "`nAll $($BROskiBrainTools.Count) BROski Brain tools registered -- AI can now call them!`n" -ForegroundColor Yellow

return $BROskiBrainTools
