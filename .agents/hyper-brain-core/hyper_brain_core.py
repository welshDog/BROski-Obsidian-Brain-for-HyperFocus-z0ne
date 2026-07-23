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
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiohttp
import uvicorn

# Windows consoles default to cp1252, which cannot encode the emoji used in
# module print()s — that crashes startup. Force UTF-8 stdio so the engine
# boots on any OS (no-op on Linux/Docker, which is already UTF-8).
import sys
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Internal modules (all async)
from focus_tracker import FocusTracker
from analytics_engine import AnalyticsEngine
from hyper_split import HyperSplitEngine
from ai_distraction_filter import DistractionFilter
from mcp_bridge import MCPBridge
from session_snapshot import SessionSnapshot
from morning_briefing_ai import MorningBriefingAI
from events_feed import EventsFeed
from gamification_summary import compute_gamification_summary
from difficulty_dial import DifficultyDial, dynamic_multiplier, session_quality_score
from distraction_monitor import DistractionMonitor
from constellation_builder import ConstellationBuilder

app = FastAPI(title="THE HYPER BRAIN", version="3.0.0")

# ─── Config ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/vault")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/4")
MCP_PORT = int(os.environ.get("MCP_PORT", "8099"))
HYPERCORE_API_URL = os.environ.get("HYPERCORE_API_URL", "")
APP_LEVEL = 20

# ─── State ────────────────────────────────────────────
focus_tracker: Optional[FocusTracker] = None
analytics: Optional[AnalyticsEngine] = None
hyper_split: Optional[HyperSplitEngine] = None
distraction_filter: Optional[DistractionFilter] = None
mcp_bridge: Optional[MCPBridge] = None
snapshot: Optional[SessionSnapshot] = None
briefing_ai: Optional[MorningBriefingAI] = None
events_feed: Optional[EventsFeed] = None
difficulty_dial: Optional[DifficultyDial] = None
distraction_monitor: Optional[DistractionMonitor] = None
constellation: Optional[ConstellationBuilder] = None

# Level 18/19 cross-wiring state.
_active_intent: Optional[str] = None          # intent of the live focus session (drift detection)
_recent_chunk_difficulty: float = 0.5         # last HyperSplit difficulty (Level 17 → 19)

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

class DifficultySet(BaseModel):
    intensity: str  # low | medium | hyper | chaos

app.mount("/ui/assets", StaticFiles(directory=WEB_DIR), name="ui-assets")

# ─── Lifespan ─────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global focus_tracker, analytics, hyper_split, distraction_filter, mcp_bridge, snapshot, briefing_ai, events_feed, difficulty_dial, distraction_monitor, constellation
    # Skill loadout boot-check — HYPER-SILLs canonical resolver (mounted). Fail-open.
    try:
        import sys as _sys
        _sys.path.insert(0, os.environ.get("HYPER_SILLS_SCRIPTS", "/hyper-sills/scripts"))
        from agent_boot import boot_check as _boot_check
        _boot_check("agent-hyper-brain-core",
                    root=os.environ.get("HYPER_SILLS_ROOT", "/hyper-sills"),
                    strict=os.environ.get("LOADOUT_STRICT", "false").lower() in ("1", "true", "yes"))
    except Exception as _e:
        print(f"[loadout] boot-check skipped: {_e}")

    focus_tracker = FocusTracker(vault_path=VAULT_PATH, redis_url=REDIS_URL)
    analytics = AnalyticsEngine(vault_path=VAULT_PATH)
    hyper_split = HyperSplitEngine(vault_path=VAULT_PATH)
    distraction_filter = DistractionFilter(vault_path=VAULT_PATH)
    mcp_bridge = MCPBridge(mcp_port=MCP_PORT, vault_path=VAULT_PATH)
    snapshot = SessionSnapshot(vault_path=VAULT_PATH, focus_tracker=focus_tracker, distraction_filter=distraction_filter)
    briefing_ai = MorningBriefingAI(vault_path=VAULT_PATH, mcp_bridge=mcp_bridge)
    events_feed = EventsFeed(maxlen=200)
    difficulty_dial = DifficultyDial(vault_path=VAULT_PATH)
    distraction_monitor = DistractionMonitor(
        vault_path=VAULT_PATH,
        distraction_filter=distraction_filter,
        snapshot=snapshot,
        difficulty_dial=difficulty_dial,
    )
    constellation = ConstellationBuilder(vault_path=VAULT_PATH)
    events_feed.add("system", "hyper_brain_startup", {"version": "3.0.0"})

    await focus_tracker.start()
    await mcp_bridge.connect()
    # Level 18 — background distraction monitor (only acts while a session is live).
    asyncio.create_task(_distraction_monitor_loop())
    print("🧠 THE HYPER BRAIN v3.0 online — Level 20")


async def _distraction_monitor_loop():
    """Level 18 — periodically check the live session for the 3 distraction signals."""
    interval = int(os.environ.get("DISTRACTION_MONITOR_INTERVAL_S", "300"))
    while True:
        try:
            await asyncio.sleep(interval)
            if distraction_monitor and distraction_filter and distraction_filter.active_session_id:
                outcome = await distraction_monitor.check(_active_intent)
                if events_feed and (outcome.get("fired") or outcome.get("nudged")):
                    events_feed.add(
                        "distraction",
                        "Level 18 check: " + ("nudged" if outcome.get("nudged") else "signals fired"),
                        {"fired": outcome.get("fired", []), "nudged": outcome.get("nudged", False)},
                    )
        except asyncio.CancelledError:
            break
        except Exception:
            pass  # never let the monitor loop crash the engine

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
        "level": APP_LEVEL,
        "containers": 30,
        "services": {
            "focus_tracker": focus_tracker is not None,
            "analytics": analytics is not None,
            "hyper_split": hyper_split is not None,
            "distraction_filter": distraction_filter is not None,
            "mcp_bridge": mcp_bridge is not None if mcp_bridge else False,
            "snapshot": snapshot is not None,
            "briefing_ai": briefing_ai is not None,
            "difficulty_dial": difficulty_dial is not None,
            "constellation": constellation is not None,
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ui")
async def ui_index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))

@app.get("/ui/toolkit")
async def ui_toolkit():
    return FileResponse(os.path.join(WEB_DIR, "toolkit.html"))

@app.get("/events")
async def events(limit: int = 10):
    if not events_feed:
        return {"events": []}
    return {"events": events_feed.list(limit=limit)}

@app.get("/gamification/summary")
async def gamification_summary():
    return await compute_gamification_summary(VAULT_PATH, level=APP_LEVEL)

# ─── Focus Sessions ───────────────────────────────────
@app.post("/focus/start")
async def focus_start(req: FocusSessionStart):
    """Start a tracked focus session with adaptive difficulty."""
    if not focus_tracker:
        raise HTTPException(503, "focus_tracker not available")
    session = await focus_tracker.start_session(
        intent=req.intent,
        estimated_minutes=req.estimated_minutes,
        project=req.project,
        tags=req.tags,
        difficulty_preference=req.difficulty_preference
    )
    global _active_intent
    _active_intent = req.intent  # Level 18 — used for topic-drift detection
    if distraction_filter:
        await distraction_filter.enable_for_session(session["id"])
    if snapshot:
        await snapshot.capture(session["id"])
    if events_feed:
        events_feed.add("focus_start", f"Focus started: {req.intent}", {"session_id": session["id"]})
    return {"session": session, "mode": "hyperfocus_activated"}

@app.post("/focus/end")
async def focus_end(req: FocusSessionEnd):
    """End session, calculate XP, update streaks, generate analytics."""
    if not focus_tracker:
        raise HTTPException(503, "focus_tracker not available")
    result = await focus_tracker.end_session(req.session_id, req.actual_minutes, req.mood)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(404, result["error"])

    # Capture distraction severity BEFORE disabling (disable clears the log).
    distraction_avg = 0.0
    if distraction_filter:
        _rec = await distraction_filter.get_recommendation()
        distraction_avg = float(_rec.get("avg_score", 0.0) or 0.0)
        await distraction_filter.disable_for_session(req.session_id)

    # Award BROski$ + XP
    if not analytics:
        raise HTTPException(503, "analytics not available")
    coins, xp = await analytics.award_for_session(result)

    # Level 19 — variable multiplier: intensity × session quality × HyperSplit chunk difficulty.
    if difficulty_dial:
        dial = await difficulty_dial.get()
        estimated = int((result or {}).get("estimated_minutes", req.actual_minutes) or req.actual_minutes)
        quality = session_quality_score(req.actual_minutes, estimated, distraction_avg, req.mood)
        multiplier = dynamic_multiplier(dial["intensity"], quality, _recent_chunk_difficulty)
        coins = int(round(coins * multiplier))
        xp = int(round(xp * multiplier))
        if isinstance(result, dict):
            result["coins_earned"] = coins
            result["xp_earned"] = xp
            result["difficulty_dial"] = dial["intensity"]
            result["quality_score"] = quality
            result["chunk_difficulty"] = _recent_chunk_difficulty
            result["xp_multiplier"] = multiplier

    # Update streaks
    streak_data = await analytics.update_streaks()

    # Generate session note in vault
    note_path = await focus_tracker.write_session_note(result, VAULT_PATH)

    # Post multiplied award to BROski economy (fail-open if not configured)
    if HYPERCORE_API_URL and coins > 0:
        try:
            async with aiohttp.ClientSession() as http:
                await http.post(
                    f"{HYPERCORE_API_URL}/broski/award",
                    json={
                        "source": "brain_focus_session",
                        "coins": coins,
                        "xp": xp,
                        "session_id": req.session_id,
                        "dial": result.get("difficulty_dial", "medium"),
                    },
                    timeout=aiohttp.ClientTimeout(total=5),
                )
        except Exception:
            pass  # local vault log still records the award

    if events_feed:
        events_feed.add(
            "focus_end",
            f"Focus ended: {result.get('intent', '')}",
            {
                "session_id": req.session_id,
                "actual_minutes": req.actual_minutes,
                "mood": req.mood,
                "coins_earned": coins,
                "xp_earned": xp,
                "dial": result.get("difficulty_dial", "medium"),
            },
        )

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
    if not snapshot:
        raise HTTPException(503, "snapshot not available")
    snap = await snapshot.capture("manual_" + datetime.now().strftime("%H%M%S"))
    background_tasks.add_task(snapshot.write_to_vault, snap)
    if events_feed:
        events_feed.add("snapshot", "Snapshot captured", {"snapshot_id": snap["id"]})
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
    # Level 17 → 19: remember this chunk's difficulty so the next focus session's
    # XP reward reflects how hard the work was.
    global _recent_chunk_difficulty
    _recent_chunk_difficulty = HyperSplitEngine.difficulty_score(tree)
    return {
        "task_tree": tree,
        "vault_path": vault_path,
        "total_micro_tasks": tree["count"],
        "chunk_difficulty": _recent_chunk_difficulty,
    }

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

@app.get("/distraction/status")
async def distraction_status():
    """Live drift status for the active session — Level 18 monitoring surface."""
    if not distraction_filter:
        raise HTTPException(503, "distraction_filter not available")
    return {
        "active_session": distraction_filter.active_session_id,
        "monitoring": distraction_filter.active_session_id is not None,
        "recommendation": await distraction_filter.get_recommendation(),
    }

@app.post("/distraction/check")
async def distraction_check():
    """Level 18 — run one monitoring pass NOW: evaluate the 3 vault signals
    (note activity, idle >15min, topic drift), feed the filter, nudge on HIGH."""
    if not distraction_monitor:
        raise HTTPException(503, "distraction_monitor not available")
    outcome = await distraction_monitor.check(_active_intent)
    if events_feed and (outcome.get("fired") or outcome.get("nudged")):
        events_feed.add(
            "distraction",
            "Level 18 manual check",
            {"fired": outcome.get("fired", []), "nudged": outcome.get("nudged", False)},
        )
    return outcome

# ─── DifficultyDial (Level 19) ────────────────────────
@app.get("/difficulty/get")
async def difficulty_get():
    """Current focus-intensity dial setting + its effects."""
    if not difficulty_dial:
        raise HTTPException(503, "difficulty_dial not available")
    return await difficulty_dial.get()

@app.post("/difficulty/set")
async def difficulty_set(req: DifficultySet):
    """Set the focus-intensity dial: low | medium | hyper | chaos."""
    if not difficulty_dial:
        raise HTTPException(503, "difficulty_dial not available")
    try:
        result = await difficulty_dial.set(req.intensity)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if events_feed:
        events_feed.add("difficulty", f"Dial set to {result['intensity']}", {})
    return result

# ─── Constellation (Level 20) ─────────────────────────
async def _build_constellation() -> Dict[str, Any]:
    """Assemble the live snapshot → graph (nodes/edges) → note + Obsidian canvas."""
    h = await health()
    g = await compute_gamification_summary(VAULT_PATH, level=APP_LEVEL)
    fs = await focus_tracker.get_current_status() if focus_tracker else {"active": False}
    data = await constellation.build(h, g, fs)
    graph = constellation.build_graph(data)
    note_path = await constellation.write_to_vault(data)
    canvas_path = await constellation.write_canvas(graph)
    if events_feed:
        events_feed.add(
            "constellation", "Live map regenerated",
            {"note": note_path, "canvas": canvas_path, **graph["counts"]},
        )
    return {"map": data, "graph": graph, "note_path": note_path, "canvas_path": canvas_path}

@app.get("/constellation/map")
async def constellation_map():
    """Level 20 — live ecosystem map as graph JSON (nodes = repos/services/modules,
    edges = connections) + auto-written Hub note + auto-generated Obsidian canvas."""
    if not constellation:
        raise HTTPException(503, "constellation not available")
    return await _build_constellation()

@app.post("/constellation/refresh")
async def constellation_refresh():
    """Rebuild the constellation map + canvas. Trigger target for the GitHub
    webhook / graph-refresh Action (no new container — pings this engine on :8100)."""
    if not constellation:
        raise HTTPException(503, "constellation not available")
    result = await _build_constellation()
    return {
        "refreshed": True,
        "counts": result["graph"]["counts"],
        "canvas_path": result["canvas_path"],
        "note_path": result["note_path"],
    }

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
    if not briefing_ai:
        raise HTTPException(503, "briefing_ai not available")
    briefing = await briefing_ai.generate(
        date=req.date,
        include_ai=req.include_ai_suggestions,
        include_forecast=req.include_focus_forecast
    )
    path = await briefing_ai.write_to_vault(briefing, VAULT_PATH)
    if events_feed:
        events_feed.add("briefing", "Briefing generated", {"vault_path": path})
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

        if events_feed:
            events_feed.add("webhook", f"GitHub {event}: {repo} #{number} {action}", {"file": fname})
        return {"received": True, "event": event, "file": fname}

    if events_feed:
        events_feed.add("webhook", f"GitHub {event}", {})
    return {"received": True, "event": event}

# ─── Main ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
