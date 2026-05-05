"""HYPER BRAIN v3.0 — Focus Tracker + DifficultyDial
Level 16 & 19 | Real-time focus tracking with adaptive sessions
"""
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import threading

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/vault"))
SESSIONS_FILE = VAULT_PATH / "HYPERFOCUS_ZONE" / "Analytics" / "sessions.json"


class DifficultyDial:
    """Dynamically adjusts task difficulty and XP based on performance + energy."""

    BASE_XP = {"easy": 10, "medium": 25, "hard": 50, "hyperfocus": 100}
    ENERGY_MULTIPLIERS = {
        range(1, 4): 0.5,   # Low energy — reduce difficulty, still earn XP
        range(4, 7): 1.0,   # Normal
        range(7, 11): 1.5   # High energy — bonus XP
    }

    def get_multiplier(self, energy: int) -> float:
        for energy_range, mult in self.ENERGY_MULTIPLIERS.items():
            if energy in energy_range:
                return mult
        return 1.0

    def calculate_xp(self, difficulty: str, energy: int, completed: bool, streak: int) -> int:
        base = self.BASE_XP.get(difficulty, 25)
        multiplier = self.get_multiplier(energy)
        streak_bonus = min(streak * 5, 50)  # Max 50 bonus XP from streak
        xp = int(base * multiplier) + streak_bonus
        return xp if completed else xp // 4  # Partial XP for incomplete sessions

    def suggest_difficulty(self, energy: int, recent_completions: int) -> str:
        if energy <= 3:
            return "easy"
        elif energy <= 6 and recent_completions < 3:
            return "medium"
        elif energy >= 7 and recent_completions >= 3:
            return "hyperfocus"
        return "medium"


class FocusSession:
    def __init__(self, task: str, duration_minutes: int = 25, energy_level: int = 5):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.task = task
        self.duration_minutes = duration_minutes
        self.energy_level = energy_level
        self.started_at = datetime.now()
        self.completed = False
        self.distractions = 0
        self.dial = DifficultyDial()

    def complete(self) -> dict:
        self.completed = True
        elapsed = (datetime.now() - self.started_at).seconds // 60
        xp = self.dial.calculate_xp(
            "medium", self.energy_level, True, streak=self._get_streak()
        )
        return {
            "session_id": self.session_id,
            "task": self.task,
            "duration_actual": elapsed,
            "duration_planned": self.duration_minutes,
            "distractions": self.distractions,
            "xp_earned": xp,
            "completed": True,
            "message": f"🎉 Session complete! +{xp} XP earned. Nice one BROski♾️!"
        }

    def _get_streak(self) -> int:
        """Load streak from analytics file."""
        try:
            analytics_file = VAULT_PATH / "HYPERFOCUS_ZONE" / "Analytics" / "streaks.json"
            if analytics_file.exists():
                data = json.loads(analytics_file.read_text())
                return data.get("current_streak", 0)
        except Exception:
            pass
        return 0

    def log_distraction(self):
        self.distractions += 1

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "task": self.task,
            "started_at": self.started_at.isoformat(),
            "duration_minutes": self.duration_minutes,
            "energy_level": self.energy_level,
            "distractions": self.distractions,
            "completed": self.completed
        }


def save_session(session: FocusSession):
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    sessions = []
    if SESSIONS_FILE.exists():
        try:
            sessions = json.loads(SESSIONS_FILE.read_text())
        except Exception:
            sessions = []
    sessions.append(session.to_dict())
    SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))
    print(f"✅ Session saved: {session.session_id}")


if __name__ == "__main__":
    print("🧠 Focus Tracker v3.0 — DifficultyDial active")
    dial = DifficultyDial()
    print(f"Energy 8, streak 5 → XP: {dial.calculate_xp('medium', 8, True, 5)}")
    print(f"Suggested difficulty (energy=3): {dial.suggest_difficulty(3, 1)}")
    print(f"Suggested difficulty (energy=9): {dial.suggest_difficulty(9, 5)}")
