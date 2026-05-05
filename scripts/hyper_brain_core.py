"""HYPER BRAIN v3.0 — FastAPI Orchestrator Core
Level 20 | Port 8100 | The 30th Container
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json
import os
import sys

app = FastAPI(
    title="THE HYPER BRAIN v3.0",
    description="Neurodivergent-first focus intelligence for the HYPERFOCUS z0ne",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VAULT_PATH = os.environ.get("VAULT_PATH", "/vault")
LEVEL = 20
CONTAINERS = 30


class FocusTask(BaseModel):
    title: str
    priority: str = "medium"  # low | medium | high | hyperfocus
    energy_level: int = 5     # 1-10
    estimated_minutes: int = 25


class SessionStart(BaseModel):
    task_title: str
    duration_minutes: int = 25
    mode: str = "pomodoro"  # pomodoro | deep | sprint | recovery


@app.get("/health")
async def health():
    return {
        "status": "hyper",
        "version": "3.0.0",
        "level": LEVEL,
        "containers": CONTAINERS,
        "timestamp": datetime.utcnow().isoformat(),
        "modules": [
            "focus_tracker",
            "ai_distraction_filter",
            "hyper_split",
            "mcp_bridge",
            "analytics_engine",
            "github_webhook_server",
            "morning_briefing_ai",
            "session_snapshot"
        ]
    }


@app.get("/status")
async def status():
    return {
        "brain": "ONLINE",
        "level": LEVEL,
        "vault_path": VAULT_PATH,
        "bottlenecks_fixed": 7,
        "levels_unlocked": list(range(13, 21))
    }


@app.post("/focus/start")
async def start_focus_session(session: SessionStart):
    return {
        "session_id": f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task": session.task_title,
        "duration": session.duration_minutes,
        "mode": session.mode,
        "started_at": datetime.utcnow().isoformat(),
        "message": f"🧠 Focus locked on: {session.task_title}. LET'S GO BROski♾️!"
    }


@app.post("/task/split")
async def split_task(task: FocusTask):
    """Trigger HyperSplit decomposition"""
    return {
        "original_task": task.title,
        "energy_level": task.energy_level,
        "message": "HyperSplit engaged — use /hyper_split endpoint for full decomposition",
        "tip": "Low energy? Start with the smallest sub-task first."
    }


@app.get("/briefing/today")
async def morning_briefing():
    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "message": "Morning Briefing AI — use morning_briefing_ai.py for full AI-powered briefing",
        "tip": "Check your top 3 priorities before opening any apps."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
