#!/usr/bin/env python3
"""
hyper_brain_core.py
THE HYPER BRAIN v3.0 — Central Orchestrator
FastAPI app coordinating all focus, AI, and sync services.
Port: 8100 (the 30th container in the Hyperfocus Zone)
BROski♾️
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Internal modules (all async)
from focus_tracker import FocusTracker
from analytics_engine import AnalyticsEngine
from hyper_split import HyperSplitEngine
from ai_distraction_filter import DistractionFilter
from mcp_bridge import MCPBridge
from session_snapshot import SessionSnapshot
from morning_briefing_ai import MorningBriefingAI

app = FastAPI(title="THE HYPER BRAIN", version="3.0.0")

# ─── Config ───────────────────────────────────────────
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/vault")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/4")
MCP_PORT = int(os.environ.get("MCP_PORT", "8099"))

# ─── State ────────────────────────────────────────────
focus_tracker: Optional[FocusTracker] = None
analytics: Optional[AnalyticsEngine] = None
hyper_split: Optional[HyperSplitEngine] = None
distraction_filter: Optional[DistractionFilter] = None
mcp_bridge: Optional[MCPBridge] = None
snapshot: Optional[SessionSnapshot] = None
briefing_ai: Optional[MorningBriefingAI] = None

# ─── Pydantic Models ──────────────────────────────────
class FocusSessionStart(BaseModel):
    intent: str
    estimated_minutes: int = 25
    project: Optional[str] = None
    tags: List[str] = []
    difficulty_preference: str = "auto"  # auto | easy | medium | hard

class FocusSessionEnd(BaseModel):
    session_id: str
    actual_minutes: int
    distractions_blocked: int = 0
    notes: str = ""
    mood: int = 5  # 1–10

class HyperSplitRequest(BaseModel):
    task_title: str
    task_description: str
    max_depth: int = 3
    target_minutes_per_task: int = 15

class DistractionReport(BaseModel):
    source: str  # app | web | notification | internal
    context: str
    timestamp: Optional[datetime] = None

class MorningBriefingRequest(BaseModel):
    date: Optional[str] = None  # YYYY-MM-DD, default today
    include_ai_suggestions: bool = True
    include_focus_forecast: bool = True

# ─── Lifespan ─────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global focus_tracker, analytics, hyper_split, distraction_filter, mcp_bridge, snapshot, briefing_ai
    focus_tracker = FocusTracker(vault_path=VAULT_PATH, redis_url=REDIS_URL)
    analytics = AnalyticsEngine(vault_path=VAULT_PATH)
    hyper_split = HyperSplitEngine(vault_path=VAULT_PATH)
    distraction_filter = DistractionFilter(vault_path=VAULT_PATH)
    mcp_bridge = MCPBridge(mcp_port=MCP_PORT, vault_path=VAULT_PATH)
    snapshot = SessionSnapshot(vault_path=VAULT_PATH)
    briefing_ai = MorningBriefingAI(vault_path=VAULT_PATH, mcp_bridge=mcp_bridge)

    await focus_tracker.start()
    await mcp_bridge.connect()
    print("🧠 THE HYPER BRAIN v3.0 online — Level 20")

@app.on_event("shutdown")
async def shutdown():
    if focus_tracker:
        await focus_tracker.stop()
    if mcp_bridge:
        await mcp_bridge.disconnect()
    print("🧠 Hyper Brain offline. Sessions saved.")

# ─── Health ───────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "hyper",
        "version": "3.0.0",
        "level": 20,
        "containers": 30,
        "services": {
            "focus_tracker": focus_tracker is not None,
            "analytics": analytics is not None,
            "hyper_split": hyper_split is not None,
            "distraction_filter": distraction_filter is not None,
            "mcp_bridge": mcp_bridge is not None if mcp_bridge else False,
            "snapshot": snapshot is not None,
            "briefing_ai": briefing_ai is not None,
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ─── Focus Sessions ───────────────────────────────────
@app.post("/focus/start")
async def focus_start(req: FocusSessionStart):
    """Start a tracked focus session with adaptive difficulty."""
    session = await focus_tracker.start_session(
        intent=req.intent,
        estimated_minutes=req.estimated_minutes,
        project=req.project,
        tags=req.tags,
        difficulty_preference=req.difficulty_preference
    )
    # Auto-enable distraction filter
    await distraction_filter.enable_for_session(session["id"])
    # Take snapshot of current vault state
    await snapshot.capture(session["id"])
    return {"session": session, "mode": "hyperfocus_activated"}

@app.post("/focus/end")
async def focus_end(req: FocusSessionEnd):
    """End session, calculate XP, update streaks, generate analytics."""
    result = await focus_tracker.end_session(req.session_id, req.actual_minutes, req.mood)
    await distraction_filter.disable_for_session(req.session_id)

    # Award BROski$ + XP
    coins, xp = await analytics.award_for_session(result)

    # Update streaks
    streak_data = await analytics.update_streaks()

    # Generate session note in vault
    note_path = await focus_tracker.write_session_note(result, VAULT_PATH)

    return {
        "session_result": result,
        "reward": {"coins": coins, "xp": xp},
        "streaks": streak_data,
        "note_path": note_path
    }

@app.get("/focus/status")
async def focus_status():
    """Current focus state + live metrics."""
    return await focus_tracker.get_current_status()

@app.post("/focus/snapshot")
async def focus_snapshot(background_tasks: BackgroundTasks):
    """Emergency session snapshot — save brain state NOW."""
    snap = await snapshot.capture("manual_" + datetime.now().strftime("%H%M%S"))
    background_tasks.add_task(snapshot.write_to_vault, snap)
    return {"snapshot_id": snap["id"], "saved": True}

# ─── HyperSplit ───────────────────────────────────────
@app.post("/hypersplit")
async def hypersplit(req: HyperSplitRequest):
    """Decompose a task into micro-tasks via recursive LLM + heuristics."""
    tree = await hyper_split.decompose(
        title=req.task_title,
        description=req.task_description,
        max_depth=req.max_depth,
        target_minutes=req.target_minutes_per_task
    )
    # Write to vault as task tree
    vault_path = await hyper_split.write_to_vault(tree, VAULT_PATH)
    return {"task_tree": tree, "vault_path": vault_path, "total_micro_tasks": tree["count"]}

# ─── Distraction Filter ───────────────────────────────
@app.post("/distraction/report")
async def report_distraction(req: DistractionReport):
    """Log a distraction for pattern analysis."""
    score = await distraction_filter.report(req.source, req.context, req.timestamp)
    return {"logged": True, "distraction_score": score, "recommendation": await distraction_filter.get_recommendation()}

@app.get("/distraction/patterns")
async def distraction_patterns(days: int = 7):
    """Weekly distraction pattern report."""
    return await distraction_filter.get_patterns(days)

# ─── Analytics ────────────────────────────────────────
@app.get("/analytics/weekly")
async def weekly_analytics():
    """Generate weekly focus report + write to vault."""
    report = await analytics.generate_weekly_report()
    path = await analytics.write_to_vault(report, VAULT_PATH)
    return {"report": report, "vault_path": path}

@app.get("/analytics/streaks")
async def streaks():
    """Current streak data + recovery tokens."""
    return await analytics.get_streaks()

@app.get("/analytics/heatmap")
async def focus_heatmap(days: int = 30):
    """Focus intensity heatmap data for visualization."""
    return await analytics.generate_heatmap(days)

# ─── Morning Briefing ─────────────────────────────────
@app.post("/briefing/generate")
async def generate_briefing(req: MorningBriefingRequest):
    """AI-powered morning briefing with predictive prioritization."""
    briefing = await briefing_ai.generate(
        date=req.date,
        include_ai=req.include_ai_suggestions,
        include_forecast=req.include_focus_forecast
    )
    path = await briefing_ai.write_to_vault(briefing, VAULT_PATH)
    return {"briefing": briefing, "vault_path": path}

# ─── MCP Bridge ───────────────────────────────────────
@app.get("/mcp/status")
async def mcp_status():
    """MCP bridge connection status."""
    if mcp_bridge:
        return await mcp_bridge.status()
    return {"connected": False}

@app.post("/mcp/query")
async def mcp_query(query: str):
    """Query vault via MCP + local LLM."""
    if not mcp_bridge:
        raise HTTPException(503, "MCP bridge not available")
    return await mcp_bridge.query_vault(query)

# ─── GitHub Webhook ───────────────────────────────────
@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Real-time GitHub webhook receiver."""
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "unknown")

    # Validate signature (HMAC)
    # ... validation logic ...

    # Write to vault immediately
    inbox_path = os.path.join(VAULT_PATH, "00-Inbox", "GitHub")
    os.makedirs(inbox_path, exist_ok=True)

    if event in ["issues", "pull_request"]:
        repo = payload.get("repository", {}).get("name", "unknown")
        action = payload.get("action", "unknown")
        number = payload.get("issue", payload.get("pull_request", {})).get("number", 0)
        title = payload.get("issue", payload.get("pull_request", {})).get("title", "")

        note = f"""---
created: {datetime.utcnow().isoformat()}
repo: {repo}
event: {event}
action: {action}
number: {number}
status: open
tags: [github, {event}, {repo}]
---
# {'🐛' if event == 'issues' else '🔀'} {repo} #{number} — {title}

**Action**: {action}
**URL**: {payload.get('issue', payload.get('pull_request', {})).get('html_url', '')}

## Details
```json
{json.dumps(payload, indent=2, default=str)[:2000]}
```
"""
        fname = f"{repo}_{event}_{number}_{action}.md"
        with open(os.path.join(inbox_path, fname), "w", encoding="utf-8") as f:
            f.write(note)

        return {"received": True, "event": event, "file": fname}

    return {"received": True, "event": event}

# ─── Main ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
