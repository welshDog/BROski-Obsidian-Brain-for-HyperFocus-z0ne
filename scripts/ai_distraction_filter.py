"""HYPER BRAIN v3.0 — AI Distraction Filter
Level 18 | Context scoring + interventions for ADHD focus protection
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/vault"))
DISTRACTION_LOG = VAULT_PATH / "HYPERFOCUS_ZONE" / "Analytics" / "distractions.json"

# Context categories and their distraction risk scores (0-10)
CONTEXT_SCORES = {
    # High focus — low distraction risk
    "coding": 2,
    "writing": 2,
    "deep_work": 1,
    "design": 3,
    # Medium risk
    "research": 4,
    "emails": 5,
    "meetings": 4,
    # High distraction risk
    "social_media": 9,
    "news": 7,
    "gaming": 8,
    "youtube": 8,
    "discord": 6,
    "reddit": 9,
    "shopping": 7,
    # Unknown
    "unknown": 5,
}

INTERVENTIONS = {
    "gentle": [
        "👀 Hey Bro, you drifted a bit — what were you working on?",
        "⏰ Pomodoro check-in: still locked in?",
        "🧠 Brain check — is this tab helping your task?",
    ],
    "medium": [
        "🚨 Distraction alert! Your focus is slipping — come back!",
        "⚡ FOCUS SHIELD ACTIVATED — close the tab, Bro!",
        "🎯 Task reminder: '{task}' needs you right now!",
    ],
    "strong": [
        "🔴 HYPERFOCUS BROKEN — 3 distractions logged this session!",
        "💪 You've got this. Close everything. One tab. One task.",
        "🧠 ADHD brain trying to escape? That's okay. Breathe. Refocus.",
    ]
}


class DistractionFilter:
    def __init__(self):
        self.distraction_count = 0
        self.session_start = datetime.now()
        self.current_task: Optional[str] = None
        self.log: list = self._load_log()

    def _load_log(self) -> list:
        if DISTRACTION_LOG.exists():
            try:
                return json.loads(DISTRACTION_LOG.read_text())
            except Exception:
                pass
        return []

    def _save_log(self):
        DISTRACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
        DISTRACTION_LOG.write_text(json.dumps(self.log, indent=2))

    def score_context(self, context: str) -> dict:
        """Score how distracting an activity/app/URL context is."""
        context_lower = context.lower()
        score = CONTEXT_SCORES.get("unknown", 5)

        for keyword, risk in CONTEXT_SCORES.items():
            if keyword in context_lower:
                score = risk
                break

        risk_level = "safe" if score <= 3 else "warning" if score <= 6 else "danger"
        return {
            "context": context,
            "score": score,
            "risk_level": risk_level,
            "should_intervene": score >= 6
        }

    def log_distraction(self, context: str, task: Optional[str] = None):
        self.distraction_count += 1
        entry = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "task": task or self.current_task,
            "count_in_session": self.distraction_count
        }
        self.log.append(entry)
        self._save_log()
        return self.get_intervention()

    def get_intervention(self) -> dict:
        if self.distraction_count <= 1:
            level = "gentle"
        elif self.distraction_count <= 3:
            level = "medium"
        else:
            level = "strong"

        import random
        messages = INTERVENTIONS[level]
        msg = random.choice(messages)
        if "{task}" in msg and self.current_task:
            msg = msg.format(task=self.current_task)

        return {
            "intervention_level": level,
            "message": msg,
            "distraction_count": self.distraction_count,
            "tip": "Take 3 breaths. Close the tab. Reopen your task." if self.distraction_count >= 3 else None
        }

    def set_task(self, task: str):
        self.current_task = task
        self.distraction_count = 0
        print(f"🎯 Focus task set: {task}")

    def get_session_report(self) -> dict:
        elapsed = (datetime.now() - self.session_start).seconds // 60
        return {
            "session_duration_minutes": elapsed,
            "total_distractions": self.distraction_count,
            "distraction_rate": self.distraction_count / max(1, elapsed),
            "focus_score": max(0, 100 - (self.distraction_count * 10)),
            "message": "🧠 Great focus!" if self.distraction_count <= 2 else "💪 Room to improve — you've got this!"
        }


if __name__ == "__main__":
    f = DistractionFilter()
    f.set_task("Build HYPER BRAIN v3.0")
    print(f.score_context("reddit"))
    print(f.score_context("coding"))
    print(f.log_distraction("twitter"))
    print(f.get_session_report())
