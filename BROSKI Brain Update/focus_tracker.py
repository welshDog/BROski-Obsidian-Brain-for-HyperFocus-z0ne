#!/usr/bin/env python3
"""
focus_tracker.py
Real-time focus session tracking with adaptive difficulty (DifficultyDial).
Monitors vault file activity, calculates flow state probability, 
and auto-adjusts session parameters for ADHD brains.
BROski♾️
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

import aiofiles
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


@dataclass
class FocusSession:
    id: str
    intent: str
    project: Optional[str]
    tags: List[str]
    started_at: datetime
    estimated_minutes: int
    difficulty: str  # auto | easy | medium | hard
    status: str  # active | paused | completed | abandoned

    # Live metrics
    file_events: int = 0
    keystroke_estimate: int = 0
    idle_seconds: int = 0
    last_activity: Optional[datetime] = None

    # Adaptive
    current_pomodoro: int = 25
    current_break: int = 5
    extensions_granted: int = 0

    # End state
    ended_at: Optional[datetime] = None
    actual_minutes: int = 0
    mood: int = 5
    flow_score: float = 0.0


class VaultEventHandler(FileSystemEventHandler):
    """Watchdog handler for vault file changes."""
    def __init__(self, tracker):
        self.tracker = tracker

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".md"):
            asyncio.create_task(self.tracker.record_activity("file_edit", event.src_path))


class FocusTracker:
    def __init__(self, vault_path: str, redis_url: str = None):
        self.vault_path = vault_path
        self.redis_url = redis_url
        self.sessions: Dict[str, FocusSession] = {}
        self.active_session_id: Optional[str] = None
        self.observer: Optional[Observer] = None
        self._idle_task: Optional[asyncio.Task] = None
        self._difficulty_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start file system watcher."""
        handler = VaultEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, self.vault_path, recursive=True)
        self.observer.start()
        self._idle_task = asyncio.create_task(self._idle_monitor())
        self._difficulty_task = asyncio.create_task(self._difficulty_dial_loop())

    async def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self._idle_task:
            self._idle_task.cancel()
        if self._difficulty_task:
            self._difficulty_task.cancel()

    async def start_session(self, intent: str, estimated_minutes: int = 25,
                          project: str = None, tags: List[str] = None,
                          difficulty_preference: str = "auto") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())[:8]

        # DifficultyDial: calculate optimal starting difficulty
        difficulty = await self._calculate_difficulty(difficulty_preference, intent)

        session = FocusSession(
            id=session_id,
            intent=intent,
            project=project,
            tags=tags or [],
            started_at=datetime.utcnow(),
            estimated_minutes=estimated_minutes,
            difficulty=difficulty,
            status="active",
            last_activity=datetime.utcnow(),
            current_pomodoro=await self._adaptive_pomodoro_length(difficulty)
        )

        self.sessions[session_id] = session
        self.active_session_id = session_id

        # Write session start note
        await self._write_start_note(session)

        return {
            "id": session_id,
            "started_at": session.started_at.isoformat(),
            "difficulty": difficulty,
            "pomodoro_minutes": session.current_pomodoro,
            "message": f"🔥 HyperFocus engaged: {intent}"
        }

    async def end_session(self, session_id: str, actual_minutes: int, mood: int = 5) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        session.ended_at = datetime.utcnow()
        session.actual_minutes = actual_minutes
        session.mood = mood
        session.status = "completed" if actual_minutes >= session.estimated_minutes * 0.5 else "abandoned"

        # Calculate flow score
        session.flow_score = self._calculate_flow_score(session)

        self.active_session_id = None

        return asdict(session)

    async def record_activity(self, activity_type: str, path: str):
        if not self.active_session_id:
            return
        session = self.sessions[self.active_session_id]
        session.file_events += 1
        session.last_activity = datetime.utcnow()
        session.idle_seconds = 0
        # Estimate keystrokes from file size delta (rough)
        session.keystroke_estimate += 50

    async def get_current_status(self) -> Dict[str, Any]:
        if not self.active_session_id:
            return {"active": False, "message": "No active session. Start one with /focus/start"}

        s = self.sessions[self.active_session_id]
        elapsed = (datetime.utcnow() - s.started_at).total_seconds() / 60

        return {
            "active": True,
            "session_id": s.id,
            "intent": s.intent,
            "elapsed_minutes": round(elapsed, 1),
            "pomodoro_target": s.current_pomodoro,
            "difficulty": s.difficulty,
            "file_events": s.file_events,
            "flow_score": round(s.flow_score, 2),
            "idle_seconds": s.idle_seconds,
            "time_blindness_alert": elapsed > s.current_pomodoro * 1.5,
            "message": "🔥 IN THE ZONE" if s.flow_score > 0.7 else "⚡ Focus steady"
        }

    async def write_session_note(self, result: Dict[str, Any], vault_path: str) -> str:
        """Write session log to 05-Focus-Sessions/"""
        sessions_dir = os.path.join(vault_path, "05-Focus-Sessions")
        os.makedirs(sessions_dir, exist_ok=True)

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        fname = f"Session_{result['id']}_{date_str}.md"
        fpath = os.path.join(sessions_dir, fname)

        note = f"""---
created: {result['started_at']}
ended: {result.get('ended_at', '')}
session_id: {result['id']}
project: {result.get('project', '')}
intent: {result['intent']}
tags: {json.dumps(result.get('tags', []))}
estimated_minutes: {result['estimated_minutes']}
actual_minutes: {result['actual_minutes']}
difficulty: {result['difficulty']}
mood: {result['mood']}
flow_score: {result['flow_score']}
file_events: {result['file_events']}
status: {result['status']}
coins_earned: {self._calculate_coins(result)}
xp_earned: {self._calculate_xp(result)}
---
# 🔥 Focus Session {result['id']} — {result['intent']}

**Project**: {result.get('project', 'None')}
**Duration**: {result['actual_minutes']}m / {result['estimated_minutes']}m estimated
**Flow Score**: {"⭐" * int(result['flow_score'] * 5)} ({result['flow_score']:.2f})
**Mood**: {result['mood']}/10

## Activity
- File edits: {result['file_events']}
- Keystroke estimate: {result.get('keystroke_estimate', 0)}
- Idle time: {result.get('idle_seconds', 0)}s

## Reflection
> {result.get('notes', '')}

---
*Logged by THE HYPER BRAIN v3.0*
"""
        async with aiofiles.open(fpath, "w", encoding="utf-8") as f:
            await f.write(note)
        return fpath

    # ─── Internal algorithms ─────────────────────────────

    async def _calculate_difficulty(self, preference: str, intent: str) -> str:
        """DifficultyDial: analyze historical data + intent complexity."""
        if preference != "auto":
            return preference

        # Heuristic: check intent keywords for complexity
        complex_keywords = ["refactor", "architecture", "design", "integrate", "migrate"]
        easy_keywords = ["fix typo", "update readme", "rename", "color"]

        intent_lower = intent.lower()
        if any(k in intent_lower for k in complex_keywords):
            return "hard"
        if any(k in intent_lower for k in easy_keywords):
            return "easy"

        # Check recent performance trend
        # (Would query analytics DB in full implementation)
        return "medium"

    async def _adaptive_pomodoro_length(self, difficulty: str) -> int:
        """ADHD-optimized Pomodoro lengths by difficulty + time of day."""
        hour = datetime.utcnow().hour
        base = {"easy": 15, "medium": 25, "hard": 45}.get(difficulty, 25)

        # Morning ADHD brains often have more sustained attention
        if 6 <= hour <= 10:
            base += 5
        # Post-lunch crash — shorter sessions
        elif 13 <= hour <= 15:
            base -= 5

        return max(10, min(60, base))

    def _calculate_flow_score(self, session: FocusSession) -> float:
        """0.0–1.0 flow state probability based on activity density."""
        if session.actual_minutes <= 0:
            return 0.0

        events_per_min = session.file_events / session.actual_minutes
        idle_ratio = session.idle_seconds / (session.actual_minutes * 60)

        # High activity + low idle = high flow
        score = min(1.0, (events_per_min / 3.0) * 0.5 + (1.0 - idle_ratio) * 0.5)
        return round(score, 2)

    def _calculate_coins(self, result: Dict) -> int:
        base = {"easy": 10, "medium": 25, "hard": 50}.get(result.get("difficulty", "medium"), 25)
        flow_bonus = int(result.get("flow_score", 0) * 30)
        mood_bonus = max(0, result.get("mood", 5) - 5) * 5
        return base + flow_bonus + mood_bonus

    def _calculate_xp(self, result: Dict) -> int:
        base = {"easy": 5, "medium": 15, "hard": 30}.get(result.get("difficulty", "medium"), 15)
        flow_bonus = int(result.get("flow_score", 0) * 20)
        return base + flow_bonus

    async def _idle_monitor(self):
        """Background task: track idle time per active session."""
        while True:
            await asyncio.sleep(5)
            if self.active_session_id:
                s = self.sessions[self.active_session_id]
                if s.last_activity:
                    idle = (datetime.utcnow() - s.last_activity).total_seconds()
                    s.idle_seconds = int(idle)

    async def _difficulty_dial_loop(self):
        """Background task: adjust difficulty every 2 minutes based on performance."""
        while True:
            await asyncio.sleep(120)
            if self.active_session_id:
                s = self.sessions[self.active_session_id]

                # If very active, offer extension
                if s.flow_score > 0.8 and s.extensions_granted < 2:
                    s.current_pomodoro += 10
                    s.extensions_granted += 1
                    # Would emit notification in full implementation

                # If idle too long, suggest break
                if s.idle_seconds > 120:
                    s.current_pomodoro = max(10, s.current_pomodoro - 5)
