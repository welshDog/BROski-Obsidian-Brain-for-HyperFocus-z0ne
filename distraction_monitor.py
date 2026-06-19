#!/usr/bin/env python3
"""
distraction_monitor.py
THE HYPER BRAIN v3.0 — Level 18 wiring

Connects SessionSnapshot's vault signals to the (passive) DistractionFilter and
fires a BROski nudge via the existing Discord relay when focus is slipping.

Three signals (per Level 18 spec):
  1. note activity  — rapid switching across many notes in a short window
  2. idle time      — > 15 min since the last vault edit
  3. topic drift    — recent edits are in a different area than the session intent

The signal evaluation is a PURE function (`evaluate_signals`) so it unit-tests
without files, Redis, or Discord. The DistractionMonitor class does the IO:
read snapshot → evaluate → feed the filter → nudge on HIGH.
BROski♾️
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import requests

IDLE_THRESHOLD_MIN = 15          # idle distraction trigger
ACTIVITY_WINDOW_MIN = 10         # window for "rapid switching"
SWITCH_THRESHOLD = 4             # distinct notes in the window => rapid switching

# PARA / vault top-level folders we treat as "areas" for drift detection.
_STOPWORDS = {"the", "a", "an", "to", "of", "and", "for", "in", "on", "my", "do", "is"}


def _top_folder(path: str) -> str:
    norm = (path or "").replace("\\", "/").lstrip("./")
    return norm.split("/", 1)[0] if "/" in norm else ""


def _intent_terms(intent: Optional[str]) -> set[str]:
    if not intent:
        return set()
    words = "".join(c.lower() if c.isalnum() else " " for c in intent).split()
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def evaluate_signals(
    recent_files: List[Dict[str, Any]],
    session_intent: Optional[str],
    now: Optional[float] = None,
    idle_threshold_min: int = IDLE_THRESHOLD_MIN,
    activity_window_min: int = ACTIVITY_WINDOW_MIN,
    switch_threshold: int = SWITCH_THRESHOLD,
) -> Dict[str, Any]:
    """Evaluate the 3 Level-18 signals from recent vault file activity.

    recent_files: [{"path": str, "mtime": epoch_seconds}, ...] (newest-first or any order).
    Returns {signals: {...}, reports: [(source, context), ...], drift_from, idle_minutes}.
    """
    now = now if now is not None else time.time()
    reports: List[tuple[str, str]] = []

    files = [f for f in (recent_files or []) if f.get("mtime")]
    most_recent = max((f["mtime"] for f in files), default=None)

    # 1. Idle time.
    idle_minutes = round((now - most_recent) / 60, 1) if most_recent else None
    idle = idle_minutes is not None and idle_minutes >= idle_threshold_min
    if idle:
        reports.append(("internal", f"idle {idle_minutes:.0f}min — no vault edits"))

    # 2. Note activity (rapid switching) — distinct notes touched in the window.
    win_cutoff = now - activity_window_min * 60
    recent_paths = {f["path"] for f in files if f["mtime"] >= win_cutoff and f.get("path")}
    rapid_switching = len(recent_paths) >= switch_threshold
    if rapid_switching:
        reports.append(("app_switch", f"rapid switching across {len(recent_paths)} notes"))

    # 3. Topic drift — dominant folder/terms of recent edits vs the session intent.
    drift = False
    drift_from = None
    terms = _intent_terms(session_intent)
    if terms and recent_paths:
        # the most-recently edited note in the window
        windowed = sorted(
            [f for f in files if f["mtime"] >= win_cutoff and f.get("path")],
            key=lambda f: -f["mtime"],
        )
        if windowed:
            top = windowed[0]["path"]
            folder = _top_folder(top)
            path_terms = {
                w for w in "".join(c.lower() if c.isalnum() else " " for c in top).split()
                if len(w) > 2 and w not in _STOPWORDS
            }
            if terms.isdisjoint(path_terms):
                drift = True
                drift_from = folder or top
                reports.append(("internal", f"topic drift — editing '{top}', intent was '{session_intent}'"))

    signals = {
        "note_activity": {"distinct_notes": len(recent_paths), "rapid_switching": rapid_switching},
        "idle": {"minutes": idle_minutes, "idle": idle},
        "topic_drift": {"drift": drift, "drift_from": drift_from},
    }
    return {
        "signals": signals,
        "reports": reports,
        "any_fired": bool(reports),
        "idle_minutes": idle_minutes,
    }


class DistractionMonitor:
    """Level 18 — wires SessionSnapshot signals → DistractionFilter → nudge."""

    def __init__(
        self,
        vault_path: str,
        distraction_filter,
        snapshot,
        difficulty_dial=None,
        nudge_webhook_env: str = "BROSKI_NUDGE_WEBHOOK",
    ) -> None:
        self.vault_path = vault_path
        self.distraction_filter = distraction_filter
        self.snapshot = snapshot
        self.difficulty_dial = difficulty_dial
        self.nudge_webhook_env = nudge_webhook_env

    async def check(self, session_intent: Optional[str] = None) -> Dict[str, Any]:
        """Run one monitoring pass. Returns signals + recommendation + nudge result."""
        recent = await self.snapshot._get_recent_files(hours=2)
        result = evaluate_signals(recent, session_intent)

        # Feed detected signals into the (passive) filter so its recommendation reflects them.
        for source, context in result["reports"]:
            await self.distraction_filter.report(source, context)

        recommendation = await self.distraction_filter.get_recommendation()

        # DifficultyDial sensitivity lowers the bar to nudge at higher intensity.
        threshold = "high"
        if self.difficulty_dial is not None:
            dial = await self.difficulty_dial.get()
            if dial.get("sensitivity", 0.6) >= 0.8:
                threshold = "medium"  # hyper/chaos — nudge sooner

        nudged = False
        level = recommendation.get("level", "none")
        if result["any_fired"] and (level == "high" or (threshold == "medium" and level in ("high", "medium"))):
            nudged = self._send_nudge(self._nudge_message(result, recommendation))

        return {
            "signals": result["signals"],
            "fired": [c for _, c in result["reports"]],
            "recommendation": recommendation,
            "nudged": nudged,
        }

    def _nudge_message(self, result: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
        tips = recommendation.get("interventions", [])
        tip = tips[0] if tips else "Take one breath and re-read your session intent."
        fired = "; ".join(c for _, c in result["reports"]) or "focus slipping"
        return f"🧠 BROski nudge — {fired}.\n👉 {tip}\nYou've got this. ♾️"

    def _send_nudge(self, message: str) -> bool:
        """Fire a Discord DM/webhook nudge (existing relay pattern). Fail-open."""
        webhook = os.getenv(self.nudge_webhook_env) or os.getenv("DISCORD_WEBHOOK_AIFS", "")
        if not webhook:
            return False
        try:
            resp = requests.post(webhook, json={"content": message}, timeout=5)
            return resp.status_code < 400
        except Exception:
            return False
